$(document).ready(function() {
	// Sends an AJAX request to like the picture with
	// the given picture id and hides the like button
	$('#like_btn').click(function() {
		var pictureIdVar;
		pictureIdVar = $(this).attr('data-pictureid');
		
		$.get('/like_picture/',
			{'picture_id': pictureIdVar},
			function(data) {
				$('#like_count').html(data);
				$('#like_btn').hide();
			})
	});
	
	// Sends an AJAX request to delete the comment with
	// the given id and removes it from the page
	$('.comment_delete_btn').click(function() {
		var commentIdVar;
		commentIdVar = $(this).attr('data-commentid');
		
		$.get('/remove_comment/',
			{'comment_id': commentIdVar},
			function(data) {
				if ( data == 0) {
					$('#cid-' + commentIdVar).remove();
				}
			})
	});
	
	// Sends an AJAX request to delete the picture with
	// the given picture id and removes it from the page
	$('.picture_delete_btn').click(function() {
		var pictureIdVar;
		pictureIdVar = $(this).attr('data-pictureid');
		
		$.get('/remove_picture/',
			{'picture_id': pictureIdVar},
			function(data) {
				if ( data == 0) {
					$('#pid-' + pictureIdVar).remove();
				}
			})
	});
});