function toggle(t){
	if(t.style.borderWidth == ""){
		t.style.borderTop = "solid";
		t.style.borderWidth = "1px";
	}else{
		t.style.borderTop = "";
		t.style.borderWidth = "0px";
	}
}

function convertDec(e) {
    var v = $("#decBox").val()+String.fromCharCode(e.keyCode);
    $("#hexaBox").val(parseInt(v).toString(16));
}


function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
$(document).ready(function() {
var act = getParameterByName('action');
if((act == null)||(act == "editsubmission")){
$('#stackdiv').show();
add();
}
});
cpt=0;
function allowDrop(ev) {
    ev.preventDefault();
}

function changeText(txt){
	var val = prompt("Valeur du block ", txt.innerHTML);
	if (val == null) {
		return;
	}
	if(txt.style.fontSize=="75%"){
		txt.style.fontSize="100%";
	}
	txt.innerHTML=val;
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var target=ev.target;
    while(target.id.substring(0,3)!="div"){
    	target=target.parentNode;
    }
    var id=(parseInt(target.id.substring(3))+1-(parseInt(target.id.substring(3))%4));
    if(data.indexOf("drag1") == -1){
    	var toto=target.id.substring(0,3)+""+id;
    	target=document.getElementById(toto);
    }
    //var val = prompt("Valeur du block ", "");

	//if (val == null) {
	//	return;
	//}
   	if(data[0]=="d"){
    	var nodeCopy = document.getElementById("f"+data).cloneNode(true);
    }else{
    	var nodeCopy = document.getElementById(data).cloneNode(true);
    }

  	nodeCopy.id = "f_"+data+"_"+cpt;
  	cpt++;
  	while (target.hasChildNodes()) {
  		target.removeChild(target.childNodes[0]);
	}
	if(data.indexOf("drag1") == -1){
		for (var i = 0; i < 4; i++) {
			var targets=document.getElementById(target.id.substring(0,3)+""+id);
			while (targets.hasChildNodes()) {
  				targets.removeChild(targets.childNodes[0]);
			}
			id++;
		}
	}else{
		var targets=document.getElementById(target.id.substring(0,3)+""+id);
		if(targets.hasChildNodes()){
			if(typeof targets.childNodes[0].id != 'undefined'){
				if(targets.childNodes[0].id.indexOf("drag1") == -1){
					while (targets.hasChildNodes()) {
  						targets.removeChild(targets.childNodes[0]);
					}
				}
			}
		}
	}
  	target.appendChild(nodeCopy);
  	var t = document.createElement("a");
  	var val="";
  	if(data.indexOf("drag1") > -1){
  		val="varname : value";
  	}
  	if(data.indexOf("drag2") > -1){
  		val="varname : value";
  	}
  	if(data.indexOf("drag3") > -1){
  		val="varname : value";
  	}
  	if(data.indexOf("drag4") > -1){
  		val="funname : @-next-ins : end-of-param : ret-val";
  	}
  	var tx = document.createTextNode(val);
 	t.setAttribute('onclick', 'javascript:changeText(this);');
  	t.appendChild(tx);
  	if(data.indexOf("drag1") == -1){
  		t.style.width= "250px";
	  	t.style.left="50px";
	  	t.style.position="absolute";
	  	t.style.top="30px";
 	  	t.style.paddingLeft="2px";
 	  	if(data.indexOf("drag4") == -1){
	  		t.style.fontSize="150%";
	  	}else{
		  	t.style.fontSize="100%";
	  	}
	  	t.style.textDecoration="none";
	  	t.style.backgroundColor="rgba(255, 255, 255, 0.75)";
	}else{
		t.style.width= "78px";
	  	t.style.left="2px";
        t.style.position="absolute";
	  	t.style.top="30px";
 	  	t.style.paddingLeft="2px";
	  	t.style.fontSize="75%";
	  	t.style.textDecoration="none";
	  	t.style.backgroundColor="rgba(255, 255, 255, 0.75)";
	}
  	target.appendChild(t);

}
function dropanddestroy(ev) {
    ev.preventDefault();
    var data = document.getElementById(ev.dataTransfer.getData("text"));
	if(data.parentNode.id!="bricks"){
    	var p=data.parentNode;
    	while (p.hasChildNodes()) {
  			p.removeChild(p.childNodes[0]);
		}
    }
}

var gifa=new Array();

function share(canvas){
    gifa.push(canvas.toDataURL('image/png'));
    gifshot.createGIF({
	    gifWidth: 400,
    	gifHeight: 520,
    	images: gifa,
    	interval: 2
	}, function (obj) {
    	if (!obj.error) {
        	var image = obj.image, animatedImage = document.createElement('img');
        	animatedImage.src = image;
        	var t=document.getElementById("gif-out");
 			while (t.hasChildNodes()) {
  				t.removeChild(t.childNodes[0]);
			}
			animatedImage.setAttribute('width',"250px");
			t.appendChild(animatedImage);
            $("#btnSave").attr("href",image);
    	}
	});
}

function add() {

	var t=document.getElementById("gif-out");
 	while (t.hasChildNodes()) {
  		t.removeChild(t.childNodes[0]);
	}
	t.setAttribute('align',"center");
	var DOM_img = document.createElement("img");
	DOM_img.src = "https://services.emi.u-bordeaux.fr/projet/git/brickstack/blob_plain/HEAD:/ajax-loader.gif";
	DOM_img.setAttribute('top-margin',"100px");
	t.appendChild(DOM_img);
	var scrollPos= document.body.scrollTop;
    html2canvas(document.getElementById("fullstack"), {
    	onrendered: function(canvas) {
            theCanvas = canvas;
        	share(canvas);
        	window.scrollTo(0,scrollPos);
    	}
    });

}



function reset() {
	while(gifa.length > 0) {
    	gifa.pop();
	}
/*	$('.feditor').css('width','300px');
	$('.editor_atto_toolbar').css('display','none');
	$('.editor_atto_content').css('overflow','');
	$('.editor_atto_content_wrap').css('border','0px');
	$('.editor_atto_content_wrap').css('background-color','');
	$("#id_onlinetext_editoreditable").html('<p><div style="border:1px solid #aaaaaa;margin:10px;width:250px; height:325px;" id="gif-out">Dernière image sauvegardée...</div></p>');
    $("#id_onlinetext_editoreditable").css('height',"353px");
    $("#id_onlinetext_editoreditable").css('width',"300px");
    $("#id_onlinetext_editoreditable").attr("contenteditable","false");
  */

	var t=document.getElementById("gif-out");
 	while (t.hasChildNodes()) {
  		t.removeChild(t.childNodes[0]);
	}
}
