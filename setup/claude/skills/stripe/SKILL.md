---
name: stripe
description: Take payments in an app with Stripe - checkout, subscriptions, webhooks. Use when an app needs to charge money, sell something, handle subscriptions, or when a payment flow is not completing.
---

# Stripe

Money makes bugs expensive. The rules below exist because each of them has
charged somebody twice or let somebody in for free.

## Pick the simplest integration that works

| Need | Use |
| --- | --- |
| Sell one thing, no app logic | **Payment Link.** No code. A URL. |
| Sell from your own app | **Checkout Session.** Stripe hosts the card form. |
| Subscriptions | **Checkout in subscription mode**, plus the Billing Portal for cancellations and card updates. |
| Custom in-page form | **Payment Element.** Only when hosted Checkout genuinely will not do. |

Do not build a custom card form to save a redirect. Hosted Checkout handles
3D Secure, wallets, local payment methods, and tax, and it keeps card data off
your servers entirely.

## Never trust the client about money

**Set the price on the server.** If the browser sends an amount, someone will
send `1`. Reference a Price ID created in the Stripe dashboard, or compute the
amount server-side from the product ID.

**Never mark an order paid because the browser reached the success page.** The
user can navigate there directly, and can also close the tab after a successful
payment. The success page is a nicety. The webhook is the truth.

## Webhooks are the source of truth

Fulfilment — granting access, sending the file, marking the order paid —
happens in the webhook handler, not in the redirect.

1. **Verify the signature** on every event with the signing secret, using the
   **raw request body**. Frameworks that parse JSON automatically break
   verification; disable body parsing on that route. An unverified endpoint
   lets anyone grant themselves anything.
2. **Handle retries.** Stripe redelivers events, and will send the same one
   more than once. Store the event id and ignore ones already processed, or
   make the handler idempotent. Without this, a retry ships the order twice.
3. **Return 200 quickly.** Acknowledge, then do slow work asynchronously.
   A slow handler gets retried, which is how duplicates start.
4. **Expect events out of order.** Do not assume the order of arrival.

The events that matter: `checkout.session.completed` for one-off purchases;
`customer.subscription.created/updated/deleted` and `invoice.paid` /
`invoice.payment_failed` for subscriptions.

## Keys

Test keys start `sk_test_` / `pk_test_`, live keys `sk_live_` / `pk_live_`.
Secret keys are server-only. A publishable key in the client is fine; a secret
key in the client is a full compromise of the account — if one is ever
committed, roll it in the dashboard immediately, because deleting the commit
does not un-leak it.

Test and live mode have entirely separate data, and separate webhook endpoints
with separate signing secrets. A webhook that works in test and not in live is
usually an endpoint that was only ever registered in test.

## Testing

Use `stripe listen --forward-to localhost:3000/api/webhook` to get events
locally, and `stripe trigger checkout.session.completed` to fire one on demand.

Test the failure paths, not just the happy one: card declined (`4000 0000 0000
0002`), 3D Secure required (`4000 0025 0000 3155`), insufficient funds. The
declined path is the one users actually hit.

Test that a duplicate webhook does not double-fulfil. That is the bug that
costs real money.

## Subscriptions

Store the Stripe customer id against your user the first time they pay, and
reuse it. Creating a second customer for an existing user splits their billing
history and breaks the portal.

Handle the states beyond active: `past_due`, `canceled`, `incomplete`,
`trialing`. Treating anything that is not `active` as "no access" cancels
people mid-trial; treating anything not `canceled` as access gives away the
product to `past_due` accounts.

Let the Billing Portal handle cancellations and card updates rather than
rebuilding it.

## Before going live

- Webhook endpoint registered in **live** mode with its own signing secret
- Live keys set on the host, test keys gone
- A real card charged, then refunded, end to end
- Receipts and the statement descriptor set — an unrecognised descriptor
  produces chargebacks
- Refund and cancellation terms written somewhere the customer can read
