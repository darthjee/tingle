<html>
<body>
@if ($user)
    <h1>Hello, {{ $user->name }}</h1>
@else
    <h1>Hello, guest</h1>
@endif
</body>
</html>
