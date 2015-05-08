<?php 
$link=mysql_connect("localhost", "root", "");

if (!$link) 
	die('Could not connect: ' . mysql_error());

mysql_select_db('freechat', $link);


function md5hash($password) {
	$salt="Random_KUGBJVY_Free chat";  
	$new_password=md5($salt.md5($password.$salt));
	return $new_password;
}

if (isset($_POST['action']) && $_POST['action'] != '') {
	$action = $_POST['action'];
	// login
	if ($action == 'login') {
		if ($_POST['username'] == NULL) {
			echo "211";
			return 1;
		}
		$username = $_POST['username'];
		$password = md5hash($_POST['password']);
		$sql="SELECT password FROM user WHERE username='$username'";
		$query=mysql_query($sql);
		$re_num = mysql_num_rows($query);
		if ($re_num == 0) {
			echo "211";
			return 1;
		}
		$result = mysql_fetch_array($query);
		if ($password == $result['password']) 
			echo "200";
		else 
			echo "210";
	}

	// register
	if ($action == 'register') {
		$username = $_POST['username'];
		$sql="SELECT * FROM user WHERE username='$username'";
		$query=mysql_query($sql);
		$re_num = mysql_num_rows($query);
		if ($re_num > 0) {
			echo "110";
			return 1;
		}
		$password = md5hash($_POST['password']);
		$mail = $_POST['mail'];
		$sql="INSERT INTO user (username, password, mail) VALUES ('$username', '$password', '$mail')";
		$query=mysql_query($sql);
		if (!$query) 
			echo "110";
		else
			echo "100";
	}
}

else {
	echo "<html>
		<h1>This is the Server for the App <i>FreeChat</i>!</h>
		</html>";
}
?>

