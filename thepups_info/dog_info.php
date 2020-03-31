<!DOCTYPE html>
<html>
<?php $env_array = parse_ini_file('cfg.ini')?>
<!--<?php define('STAGE', 'dev'); ?>-->
<head>
    <?php include("./common_head.html") ?>
</head>
<body>
<?php include("./common_nav.html") ?>
<div class="container">
    <!-- Example row of columns -->
    <div class="row">
        <div class="col-md-12">
            <h2>Dog Info 1</h2>
            <?php include("https://" . $env_array['STAGE'] . "-the-pups-snippets-2020.s3.amazonaws.com/dog_info.html") ?>
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