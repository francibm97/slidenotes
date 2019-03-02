jQuery("body").hasClass("index") &&
(function($) {
	"use strict";

	// Smooth scrolling con jQuery easing
	$('a[href*="#"]:not([href="#"])').click(function() {
		if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
			var target = $(this.hash);
			target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
			if (target.length) {
				$('html, body').animate({
					scrollTop: (target.offset().top)
				}, 1000, "easeInOutExpo");
				return false;
			}
		}
	});

	/***************************
	 *      GESTIONE FORM      *
	 ***************************/

	$("form").each(function(){ this.reset(); });

	/* CREAZIONE ELEMENTI */

	// Crea lo slider
	noUiSlider.create($("#percentage-slider").get(0),  {
		start: 50,
		step: 1,
		range: {
			min: 45,
			max: 55
		},
		pips: {
			mode: 'values',
			values: [45, 50, 55],
			density: 10
		}
	});

	/* GESTIONE ELEMENTI COLLEGATI */

	// Gestisci checkbox privacy tenendo i checkbox sulla privacy
	// sincronizzati e salvando in un cookie il valore
	$(".privacy-checkbox").change(function() {
		$(".privacy-checkbox").not($(this)).prop("checked", this.checked);
		Cookies.set("privacy-checkbox", this.checked, { expires: 365 });
	});
	if(Cookies.get("privacy-checkbox") === "true"){
		$(".privacy-checkbox").prop("checked", true);
	}

	// Collega slider con le slide nell'anteprima di output
	$("#percentage-slider").get(0).noUiSlider.on("update", function (values) {
		$("#output-page-preview .slide").css({"width": 92 - (parseInt(values[0]) - 50) * 2 + "px", "height": 69 - (parseInt(values[0]) - 50) * 1 + "px"});
		$("#percentage").val(parseInt(values[0]));
	});

	// Collega radio button con le slide nell'anteprima di output
	$(':radio[name="npage"]').change(function() {
		var elems = $("#output-page-preview .slide");
		switch(parseInt($(this).filter(':checked').val())){
			case 1:
				elems.eq(1).fadeOut(300);
				elems.eq(2).fadeOut(300);
				break;
			case 2:
				elems.eq(1).fadeIn(300).removeClass("second-third").addClass("second-half");
				elems.eq(2).fadeOut(300);
				break;
			case 3:
				elems.eq(1).fadeIn(300).removeClass("second-half").addClass("second-third");
				elems.eq(2).fadeIn(300);
				break;
		}
	});

	// Collega radio button con le slide nell'anteprima di input
	$(':radio[name="layout"]').change(function() {
		var elems = $("#input-page-preview .slide");
		var elem = $("#input-page-preview");
		switch(parseInt($(this).filter(':checked').val())){
			case 1:
				elem.removeClass("page-a4-small").addClass("page-43-small");
				elems.eq(0).removeClass("slide-top-in-a4-small").addClass("slide-single-in-43-small");
				elems.eq(1).fadeOut(300);
				break;
			case 2:
				elem.removeClass("page-43-small").addClass("page-a4-small");
				elems.eq(0).removeClass("slide-single-in-43-small").addClass("slide-top-in-a4-small");
				elems.eq(1).delay(150).fadeIn(300);
				break;
		}
	});

	// Collega radio button layout input al checkbox trim
	$(':checkbox[name="trim"]').each(function(){
		$(this).data("checked", this.checked);
	});
	$(':checkbox[name="trim"]').on("change", function(){
		$(this).data("checked", this.checked);
	});
	$(':radio[name="layout"]').change(function() {
		switch(parseInt($(this).filter(':checked').val())){
			case 1:
				$(':checkbox[name="trim"]').prop("disabled", false);
				$(':checkbox[name="trim"]').each(function(){
					$(this).prop("checked", $(this).data("checked"));
				});
				break;
			default:
				$(':checkbox[name="trim"]').prop("disabled", true);
				$(':checkbox[name="trim"]').prop("checked", false);
				break;
		}
	});

	/* GESTIONE INPUT FILE */

	// Gestisci etichetta input file
	function updateFileLabel(input) {
		if(input.val() != ''){
			var filename = input.val();
			var separator = filename[1] == ":" ? "\\" : "/";
			var base = new String(filename).substring(filename.lastIndexOf(separator) + 1);
			input.siblings(".custom-file-label").html(base);
		}
		else {
			input.siblings(".custom-file-label").html(input.siblings(".custom-file-label").data("default-text"));
		}
	}
	$(":file.custom-file-input").each(function(){
		$(this).siblings(".custom-file-label").eq(0).data("default-text", $(this).siblings(".custom-file-label").html());
	});
	$(":file.custom-file-input").on("change",function(){
		updateFileLabel($(this));
	});

	// Gestisci controllo file col server
	function readChunked(a,b,c){function d(){var i=a.slice(g,g+1048576);h.readAsBinaryString(i)}var e=a.size,g=0,h=new FileReader;h.onload=function(){return h.error?void c(h.error||{}):(g+=h.result.length,b(h.result,g,e),g>=e?void c(null):void d())},h.onerror=function(i){c(i||{})},d()}
	function getSHA256(a,b){return new Promise(function(c,d){var e=CryptoJS.algo.SHA256.create();readChunked(a,function(f,g,h){return e.update(CryptoJS.enc.Latin1.parse(f)),b&&b(g/h)},function(f){if(f)d(f);else{var g=e.finalize(),h=g.toString(CryptoJS.enc.Hex);c(h)}})})}

	$(".input-file").on("change",function(){

		$(".input-file").siblings('[name="sha256"]').val("");
		$(".input-file").prop("required", true);

		// Update di tutti gli altri input file col file selezionato
		var currentInputFile = $(this);
		$(".input-file").not(currentInputFile).each(function(){
			var newInputFile = currentInputFile.clone(true);
			newInputFile.attr("id", $(this).attr("id"));
			newInputFile.removeClass("is-invalid");
			newInputFile.insertAfter($(this));
			$(this).remove();
			updateFileLabel(newInputFile);
		});

		if($(this).val() != '' && window.Promise){
			getSHA256(this.files[0], function(p){if(p!=1) console.log("Hashing " + p * 100 + "%")})
				.then(
					function(res){
						console.log("Hashing completed");
						console.log(res);
						$(".input-file").siblings('[name="sha256"]').val(res);
						$.getJSON(currentInputFile.closest(".form-file").data("file-cache-url") + res)
							.done(function (data){
								if(data["success"] && data["data"]["cached"] == true){
									console.log("The selected file is already on the server and won't be uploaded again");
									$(".input-file").val("");
									$(".input-file").prop("required", false);
								}
							});
					},
					function(err){
						console.error("Hashing failed");
						console.error(err);
					}
				);
		}
	});

	// Drag & Drop file
	try {

		// feature detection; solleva un'eccezione se la proprietà è readonly
		$(".input-file")[0].files = null;

		$("body")
		.on("dragover", function(e){
			e.preventDefault();
			$("body>div:first-child").addClass("dragover d-flex").fadeIn(300);
		});
		$("body>div:first-child").on("dragleave", function(e){
			e.preventDefault();
			$("body>div:first-child").stop(true).removeClass("dragover d-flex").hide();
		});
		$("body>div:first-child").on("drop", function(e){
			e = e.originalEvent;
			e.preventDefault();
			$(".input-file")[0].files = e.dataTransfer.files;
			$(".dragover").removeClass("dragover d-flex").hide();
		});
	} catch(e){}

	/* VALIDAZIONE FORM */

	$(".form-file").each(function(){
		$(this).validate({
			errorPlacement: function(error,element) {
				return true;
			},
			highlight: function(element) {
				$(element).addClass("is-invalid");
			},
			unhighlight: function(element) {
				$(element).removeClass("is-invalid");
			}
		});
	});

	/* GESTIONE DELLA MODAL VISUALIZZATA AL TERMINE DELL'ELABORAZIONE O IN CASO DI ERRORE */

	function showModal(dataContent, downloadUrl) {
		$("#modal").find(".modal-title").html($("#modal").find(".modal-title").data(dataContent));
		$("#modal").find(".modal-body").html($("#modal").find(".modal-body").data(dataContent));
		// in caso di errore è undefined
		if(downloadUrl !== undefined){
			$("#modal .btn-primary").show().parent().attr("action", downloadUrl);
		}
		else {
			$("#modal .btn-primary").hide();
		}
		$("#modal").modal("show");
	}

	/* GESTIONE DELLE PROGRESS BAR E DEL BLOCCO DEI CONTROLLI DEL FORM */

	function freezeFormFile() {
		$('.form-file input, .form-file button').prop("disabled", true);
	}

	function unfreezeFormFile() {
		$('.form-file input, .form-file button').prop("disabled", false);
		// Gestisci collegamento layout id e checkbox trim
		$(':radio[name="layout"]').change();
	}

	function showProgressBar(formElement, status, progress) {
		var statuses = ["uploading", "pending", "processing", "no-connection"];
		$(formElement).find(".progress-wrapper").slideDown(300);
		$(formElement).find(".progress-label").html($(formElement).find(".progress-label").data("text-" + status));
		for(var i = 0; i < statuses.length; i++){
			$(formElement).find(".progress-bar").removeClass($(formElement).find(".progress-label").data("color-" + statuses[i]));
		}
		$(formElement).find(".progress-bar").addClass($(formElement).find(".progress-label").data("color-" + status))
		// In caso di pending o no-connection è undefined
		if(progress !== undefined) {
			$(formElement).find(".progress-bar").css("width", progress + "%");
			$(formElement).find(".progress-value").html(progress.toFixed(0) + "%");
		}
		else {
			$(formElement).find(".progress-value").html("");
		}
	}

	function hideProgressBar(formElement) {
		$(formElement).find('.progress-wrapper').slideUp(300);
		$(formElement).find(".progress-bar").css("width", "0%");
		$(formElement).find(".progress-value").html("0%");
	}

	// Funzioni richiamate dalla parte ajax per aggiornare i form

	function formJobStart(formElement) {
		freezeFormFile();
		showProgressBar(formElement, "uploading", 0);
		$(window).on("beforeunload", function(){
			return "No no non mi lasciare, amore mio ti amo";
		});
	}

	function formJobProgress(formElement, status, progress) {
		showProgressBar(formElement, status, progress);
	}

	function formJobEnd(formElement, dict) {
		$(window).off("beforeunload");
		if (dict.status == "error") {
			showModal(dict.error);
			hideProgressBar(formElement);
			unfreezeFormFile();
		}
		else {
			window.location.assign($(formElement).data("file-download-url") + dict.taskId);
			formJobProgress(formElement, "processing", 100);
			setTimeout(function(){
				hideProgressBar(formElement);
				unfreezeFormFile();
				if ($(formElement).find(".input-file").val() != ""){
					$(formElement).find(".input-file").trigger("change");
				}
			}, 1000);
			setTimeout(function(){
				showModal("job-completed", $(formElement).data("file-download-url") + dict.taskId);
			}, 250);
		}
	}

	/* GESTIONE AJAX DEI FORM */

	$.ajaxSetup({
		cache: false,
		timeout: 5000
	});

	$(".form-file").submit(function(e) {
		if(window.FormData !== undefined && $(this).valid()){
			e.preventDefault();

			var formElement = this;
			var actionUrl =  $(formElement).attr("action");
			var formData = new FormData(formElement);

			formJobStart(formElement);

			$.ajax({
				type: "POST",
				url: actionUrl,
				data: formData,
				contentType: false,
				processData: false,
				timeout: 0,
				headers:{
					"Accept": "application/json"
				},
				xhr: function(){
					var myXhr = $.ajaxSettings.xhr();
					if(myXhr.upload){
						if(formData.get) {
							if(formData.get("file").name == ""){
								return myXhr;
							}
						}
						myXhr.upload.addEventListener('progress', function(e){
							var percentage = (e.loaded * 100) / e.total;
							formJobProgress(formElement, "uploading", percentage);
						}, false);
					}
					return myXhr;
				},
				success: function(data) {
					if(data['success']){
						(function checkTaskProcessing(taskId, retry){
							$.getJSON($(formElement).data("file-status-url") + taskId)
								.done(function(data){
									if(data['success']){
										if(data['data']['status'] == 'FAILURE'){
											console.error("The server reported this job as failed");
											formJobEnd(formElement, {status: "error", error: "job-error"});
											return;
										}
										if(data['data']['status'] == 'SUCCESS'){
											formJobEnd(formElement, {status: "success", taskId: taskId});
											return;
										}
										if(data['data']['status'] == 'PROCESSING'){
											formJobProgress(formElement, "processing", data['data']['progress']);
										}
										if(data['data']['status'] == 'PENDING'){
											formJobProgress(formElement, "pending");
										}
										setTimeout(function() { checkTaskProcessing(taskId, 0); }, 1000);
									}
								})
								.fail(function(jqxhr, textStatus, error){
									if(retry > 10){
										if (jqxhr.readyState == 4) {
											console.error("Could not check job status, server error. " + textStatus);
											formJobEnd(formElement, {status: "error", error: "server-error"});
										}
										else if (jqxhr.readyState == 0) {
											console.error("Could not check job status, network error");
											formJobEnd(formElement, {status: "error", error: "network-error"});
										}
										else {
											console.error("Could not check job status, unknown error");
											formJobEnd(formElement, {status: "error", error: "server-error"});
										}
									}
									else{
										formJobProgress(formElement, "no-connection");
										setTimeout(function() { checkTaskProcessing(taskId, retry + 1); }, 5000);
									}
									return;
								});
						})(data['data']['task_id'], 0);
					}
					else {
						console.error("The server returned an unexpected result " + data);
						formJobEnd(formElement, {status: "error", error: "server-error"});
					}
				},
				error: function(jqxhr, textStatus, error){
					if (jqxhr.readyState == 4) {
						console.error("Could not complete the upload, server error. " + textStatus);
						formJobEnd(formElement, {status: "error", error: "server-error"});
					}
					else if (jqxhr.readyState == 0) {
						console.error("Could not complete the upload, network error");
						formJobEnd(formElement, {status: "error", error: "network-error"});
					}
					else {
						console.error("Could not complete the upload, unknown error");
						formJobEnd(formElement, {status: "error", error: "server-error"});
					}
				},
			});

		}
	});

})(jQuery);
