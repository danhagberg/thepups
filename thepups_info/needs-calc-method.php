<!DOCTYPE html>
<html>
<head>
		<?php include("./common_head.html") ?>
</head>
<body>
	<?php include("./common_nav.html") ?>
		<div class="container">
	
	Shift needs are calculated based on the following criteria:
		<ul>
			<li>Sessions: Each session is 35 minutes. Assuming the 10 minutes for reading and writing DBS notes, 5 minutes misc,  and 20 minutes with the dog. Each shift is divided by the number of sessions and rounded down, meaning if there are 3.6 sessions in a shift, it will show as 3.</li>
			<li>Capacity: The number of each DBS is multiplied by the number of sessions to determine the number of dogs per level that can be taken out.</li>
			<li>Needs: The number of dogs in each level is subtracted from the corresponding capacity.  The following adjustments are made to dog counts prior to subtracting:
				<ul>
					<li>Red-Team dogs are counted as 2 and added to the Purple count as they often require two people for a portion of the time.</li>
					<li>Kennel Cough dogs are counted as 1.5 as they require additional time to find and put on the PPE gear.</li>
				</ul>
			<li>Levels that do not have enough coverage are covered by the next level up. For example, if Green dogs are not covered,  then they are covered by Blue if there is extra capacity.  If none at the Blue level, then Purple will be checked.  If dogs cannot be covered by current capacity, then a need is created for that level.</li>
		</ul>
	</div>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="js/vendor/jquery-1.11.0.min.js"><\/script>')</script>
    <script src='js/vendor/bootstrap-3.1.1.min.js'></script>
    <script src='js/main.js'></script>
</body>
</html>