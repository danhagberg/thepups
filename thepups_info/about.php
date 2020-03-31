<!DOCTYPE html>
<html>
<head>
		<?php include("./common_head.html") ?>
</head>
<body>
	<?php include("./common_nav.html") ?>
	<div class="container">
		<h1>About</h1>
		Information regarding the current dogs on campus and number of volunteers currently scheduled for each shift.
		
		<h2>Release Notes</h2>
		
		<h3>1.4 - Days on Campus Stats Page</h3>
		
		<div>New page to show numbers of days on campus statistics.  Includes all population during reporting period as well as breakdowns by age and weight.</div>

		<h3>1.3 - Dog Count Adjustments</h3>
		
		<div>Increased Red - Team dog weight from 1.5 to 2.  So each Red - Team dog now counts as 2 dogs.  Also added weight of 1.5 for Kennel Cough dogs, so each will now count as 1.5 dogs, rounded up to the next whole number. This should allow extra time for finding the gear and suiting up. </div>

		<h3>1.2 - Shift Session Adjustments</h3>
		
		<div>Increased shift session from 30 minutes to 35 to reduce the number of sessions per shift. This is to better reflect the number of dogs getting out per shift.</div>
		
		<h3>1.1 - Need Adjustments</h3>
		
		<div>Modified shift needs calculation to allow for manual modifications to results based on temporary events. For example, training during a shift where the trainer will be present, but unavailable to walk dogs.</div>
		
		<h3>1.0 - Initial Release</h3>
		
		<div>Initial deployment of page layout with columns for dog counts, shift counts, and shift needs.  Additional page with info about each dog currently on campus.</div>
		
		
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