<!DOCTYPE html>
<html>
<?php include("./cfg.php")?>
<head>
    <?php include("./common_head.html") ?>
</head>
<body>
<?php include("./common_nav.html") ?>
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h3>Dogs on Campus Stats</h3>
			<p>
			Breakdown of dogs on campus by various levels.
			</p>
			<b>Report Period: <?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/report_period.html") ?></b>
			<hr>
			<h4>All Dogs</h4>
			<div class="stats_table">
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_all_dogs_table.html") ?>
			</div>
			<hr>
			<h4>History of Dogs on Campus by Group</h4>
			<div class="stats_table">
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_group_table.html") ?>
			</div>
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_group_chart.html") ?>
			<hr>
			<h4>History of DBS Dogs on Campus by Level</h4>
			<div class="stats_table">
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_dbs_level_table.html") ?>
			</div>
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_dbs_level_chart.html") ?>
			<hr>
			<h4>History of Staff Only Dogs on Campus by Level</h4>
			<div class="stats_table">
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_staff_level_table.html") ?>
			</div>
				<?php include("https://" . $STAGE . "-the-pups-snippets-2020.s3.amazonaws.com/dogs_on_campus/stats_by_staff_level_chart.html") ?>
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
