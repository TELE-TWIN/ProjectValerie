<!--
/content/custom/MediaInfo/Content.tpl 
-->

<table align="center" id="main_table" width="100%">
	<tr>
	<td valign="top" align="center" style="background-color:#AAAAAA;">
		<br />
		<!-- CUSTOM_IMAGE -->
		<br><br>
		<input type="button" name="changeBackdrop" value="change Poster" onclick="javascript:changePictures('poster');">
		<br /><br />
		<!-- CUSTOM_BACKDROP -->
		<br><br>
		<input type="button" name="changeBackdrop" value="change Backdrop" onclick="javascript:changePictures('backdrop');">
		<div id=special_features>
		<br><br><br><br>
		special Features:
		<br><br>
		<input type="button" name="changeImdbid" id="changeImdbid" value="change ImdbId" onclick="javascript:showAlternatives();">
		</div>
	</td>
	<td>
		<table align="center" id="details_table">
			<!-- CUSTOM_FORM -->
		</table>
	</td></tr>
</table>
