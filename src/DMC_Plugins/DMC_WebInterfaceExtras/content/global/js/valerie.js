function get_params(){
	var searchString = document.location.search;

	searchString = searchString.substring(1);

	var nvPairs = searchString.split("&");
	var result = new Array();
	for (var i = 0; i < nvPairs.length; i++){
		 var nvPair = nvPairs[i].split("=");
		 if (typeof(nvPair[1]) != "undefined") {
			result[decode_utf8(unescapeMe(nvPair[0]))] = decode_utf8(unescapeMe(nvPair[1]));
		 }
	}
	return result;
}

function unescapeMe(str) {
     return unescape(str.replace(/\+/g, " "));
}

function encode_utf8( s )
{
  return unescape( encodeURIComponent( s ) );
}

function decode_utf8( s )
{
  return decodeURIComponent( escape( s ) );
}

function blink( element )
{
  $(element).animate(
  { opacity: 0.15 }, "fast", "swing").animate(
	{ opacity: 1 }, "fast", "swing");
}
