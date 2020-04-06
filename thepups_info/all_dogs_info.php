<!DOCTYPE html>
<html>
<?php include("./cfg.php")?>
<head>
    <?php include("./common_head.html") ?>
    <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>
    <link rel='stylesheet' href='https://cdn.datatables.net/1.10.20/css/dataTables.bootstrap.min.css'>
</head>
<body>
<?php include("./common_nav.html") ?>
<div class="container">
    <!-- Example row of columns -->
    <div class="row">
        <div class="col-md-12">
            <h2>All Dogs</h2>
			<b>Report Period: <?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/all_dog_info_report_period.html") ?></b>
			<p>
			Values are from last day on campus
			<hr>
            <?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/all_dog_info.html") ?>
        </div>
    </div>

    <hr>

    <footer>
        <p>&copy; Dan Hagberg 2020</p>
    </footer>
</div>
<!-- /container -->
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<script>window.jQuery || document.write('<script src="js/vendor/jquery-1.11.0.min.js"><\/script>')</script>
<script src='js/vendor/bootstrap-3.1.1.min.js'></script>
<script src='js/main.js'></script>
<script src='https://code.jquery.com/jquery-3.3.1.js'></script>
<script src='https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js'></script>
<script src='https://cdn.datatables.net/1.10.20/js/dataTables.bootstrap.min.js'></script>
<script>
$(document).ready(function() {
    $('#dog_info').DataTable();
} );
</script>
</body>
</html>
