<!DOCTYPE html>
<html>
<body>
<?php function title(string $t): string { return $t !== '' ? $t : 'Untitled'; } ?>
<h1><?= title('Home') ?></h1>
<?php if (isset($user)): ?>
  <p>Welcome back</p>
<?php else: ?>
  <p>Please log in</p>
<?php endif; ?>
</body>
</html>
