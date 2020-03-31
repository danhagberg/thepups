<!DOCTYPE html>
<html>
<?php $env_array = parse_ini_file('cfg.ini')?>
<head>
		<?php include("./common_head.html") ?>
</head>
<body>
	<?php include("./common_nav.html") ?>
	<div class="container">
	      <!-- Example row of columns -->
	      <div class="row">
			<div class="col-md-4">
				<h2>DBS Dog Counts</h2>
		         <?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dbs_dog_counts.html") ?>
				 <br>
				
				<h2>Staff/BPA Dog Counts</h2>
				  <?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/staff_dog_counts.html") ?>
				<br>
				
				<p><a class="btn btn-default" href="./dog_info.php" role="button">View details &raquo;</a></p>
				
				<br>
				<em>Dog counts current as of <?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dog_count_timestamp.html") ?> </em>
			</div>
			
			<div class="col-md-4">
				<h2>Shift Counts *</h2>
				<?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dbs_shift_counts.html") ?>
				<br>
				<em>* No Green DBS volunteers during the shelter shutdown.</em>
				<br>
				<em>Shift counts current as of <?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dbs_shift_counts_timestamp.html") ?> </em>
			</div>
			
			<div class="col-md-4">
				<h2>Needs</h2>
				<?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dbs_shift_needs.html") ?>
				<br>
				<h4>Notes on Shift Needs</h4>
				<p><em>Needs are calculated for the next 5 days based on the current number of dogs.  Dog counts are updated every morning and will be reflected here.  Shift counts will be updated every couple of days.</em></p>
				<p><em>Needs are minimum handling level. For example, if we need 2 greens and 1 purple, then we need at least 1 Purple DBS and 2 of any combination of Green, Blue, or Purple DBS.</em></p>
				
				<p><a class="btn btn-default" href="./needs-calc-method.php" role="button">View Calculation Info &raquo;</a></p>
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
