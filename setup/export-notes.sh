#!/usr/bin/env bash
# Export every note from the Apple Notes app into plain-text files.
#
# Run ON THE MAC — Apple Notes is only readable from the machine itself:
#
#   bash setup/export-notes.sh              # writes to ~/notes-export
#   bash setup/export-notes.sh some/dir     # writes there instead
#
# First run: macOS asks "Terminal wants access to control Notes" — click OK.
# (If you clicked Don't Allow once, re-enable it in System Settings →
# Privacy & Security → Automation → Terminal → Notes.)
#
# Locked (password-protected) notes can't be read and are skipped by name.
# The export is yours to commit wherever you like — keep it OUT of public
# repos; notes are private by default.

set -euo pipefail

out="${1:-$HOME/notes-export}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"

echo "Exporting Apple Notes to $out ..."

NOTES_OUT="$out" osascript -l JavaScript <<'JXA'
ObjC.import('Foundation');
const notesApp = Application('Notes');
const outDir = $.getenv('NOTES_OUT');
const used = {};
let saved = 0, skipped = 0;

function safeName(name, fallback) {
  let s = (name || '').replace(/[\/\\:*?"<>|]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 80);
  if (!s) s = fallback;
  if (used[s] !== undefined) { used[s] += 1; s = s + ' ' + used[s]; }
  else { used[s] = 1; }
  return s;
}

const notes = notesApp.notes();
for (let i = 0; i < notes.length; i++) {
  try {
    const n = notes[i];
    const body = n.body();            // HTML; throws on locked notes
    const file = outDir + '/' + safeName(n.name(), 'note-' + (i + 1)) + '.html';
    $(body).writeToFileAtomicallyEncodingError(file, true, $.NSUTF8StringEncoding, null);
    saved++;
  } catch (e) {
    skipped++;
  }
}
console.log('saved ' + saved + ' notes' + (skipped ? ', skipped ' + skipped + ' (locked or unreadable)' : ''));
JXA

# Convert the HTML bodies to readable plain text with the macOS built-in.
find "$out" -name '*.html' | while IFS= read -r f; do
  textutil -convert txt "$f" -output "${f%.html}.txt" && rm "$f"
done

count="$(find "$out" -name '*.txt' | wc -l | tr -d ' ')"
echo "Done: $count text files in $out"
echo "They are NOT in any repo yet — commit them somewhere private if you want them versioned."
