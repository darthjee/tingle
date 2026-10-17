# Smoke-test fixture
Create `docker/php_complexity/fixture/` with every file from image.md §9.1, byte for byte: `Anon.php`, `CVS/legacy.php`, `Calculator.php`, `Modern.php`, `Shapes.php`, `UPPER.PHP`, `attr_anon.php`, `bom.php`, `bootstrap.php`, `broken.php`, `crlf.php`, `dup_a.php`, `dup_b.php`, `empty.php` (0 bytes), `helpers.php`, `latin1.php`, `lenient.php`, `page.php`, `welcome.blade.php` and `notes.txt`. Do not create `missing.php`.

Generate `crlf.php`, `bom.php` and `latin1.php` with the exact `printf` commands in §9.1. Add `fixture/.gitattributes` with `* -text` (as in `docker/js_complexity/fixture/.gitattributes`) so git keeps the CRLF, BOM and Latin-1 bytes. Check the result with `xxd`/`file`.

## Files to Change
- `docker/php_complexity/fixture/**` — new, the 20 fixture files plus `.gitattributes`.
