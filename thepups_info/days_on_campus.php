<!DOCTYPE html>
<html>
<?php $env_array = parse_ini_file('cfg.ini')?>
<head>
    <?php include("./common_head.html") ?>
</head>
<body>
<?php include("./common_nav.html") ?>
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h3>Total Days on Campus</h3>
			<p>
			Total days is defined as days during period in which the dog showed up on the exercise list. Days may or may not be continuous.
			</p>
			<b>Report Period: <?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/report_period.html") ?></b>
			<hr>
			<h4>All Dogs</h4>
			<div class="stats_table">
				<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_on_campus_table.html") ?>
			</div>
			<hr>
			<h4>Total Days on Campus by Age</h4>
			Days on campus broken out by age group
			<div class="stats_table">
				<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_on_campus_by_age_table.html") ?>
			</div>
				<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_on_campus_by_age_chart.html") ?>
			<hr>
			<h4>Total Days on Campus by Weight</h4>
			Days on campus broken out by weight group
			<div class="stats_table">
				<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_on_campus_by_weight_table.html") ?>
			</div>
				<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_on_campus_by_weight_chart.html") ?>
            <!--<?php include("https://prod-the-pups-snippets-2020.s3.amazonaws.com/days_on_campus/days_histogram_chart.html") ?>-->
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
</body>
</html>
