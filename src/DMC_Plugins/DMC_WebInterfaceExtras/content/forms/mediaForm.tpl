<form action="/action" method="get">
			<input type="hidden" name="type" value=%s>
			<input type="hidden" name="mode" value="%s">
			<input type="hidden" Id="Id" name="Id" value="%s">
			
			
			<tr id="tr_partentid"><td>ParentId:</td><td><input type="text" Id="ParentId" name="ParentId" value="%s"></td><td>(identifies the tvshow of this episode)</td></tr>
			<tr id="tr_type"><td>Type:</td><td id="td_type">
				<input id="type" name="Type" type="text" size="10" value="%s" disabled="disabled"></input>
				<input id="id2" name="id2" type="text" size="10" value="%s" disabled="disabled"></input> </td></tr> 
			<tr id="tr_imdbid"><td>ImdbId:</td><td>
				<input id="imdbid" name="ImdbId" type="text" size="10" value="%s" class="requiredlabel"></input></td><td>(e.g. tt9000000)</td></tr>
			<tr id="tr_thetvdbid"><td>TheTvDbId:</td><td>
				<input id="thetvdbid" name="TheTvDbId" type="text" size="10" value="%s" class="requiredlabel"></input></td><td>(e.g. 999999)</td></tr>
			<tr id="tr_title" class="small requiredlabel"><td>Title:</td><td>
				<input id="title" name="Title" type="text" class="medium requiredfield" value="%s"></input></td><td>(e.g. my title)</td></tr>
			<tr id="tr_tag"><td>Tag:</td><td>
				<input id="tag" name="Tag" type="text" value="%s" class="medium"></input></td><td>(e.g.my tag)</td></tr>
			<tr id="tr_season"><td>Season:</td><td>
				<input id="season" name="Season" type="text" maxlength="2" value="%s" class="small center"></input>
				&nbsp;&nbsp;&nbsp;&nbsp;Disc:&nbsp;
				<input id="disc" name="Disc" type="text"  maxlength="2" value="%s" class="small center"></input>
				&nbsp;&nbsp;&nbsp;&nbsp;Episode:&nbsp;
				<input id="episode" name="Episode" type="text" maxlength="3" value="%s" class="small center"></input>
				-&nbsp;<input id="episodelast" name="EpisodeLast" type="text" maxlength="3" value="%s" class="small center"></input>
			</td><td>(e.g. 01)</td></tr>
			<!--
			<tr id="tr_episode"><td>Episode:</td><td>
				<input id="episode" name="Episode" type="text" maxlength="3" value="s" class="small"></input></td><td>(e.g. 01)</td></tr>
			-->
			<tr id="tr_plot"><td>Plot:</td><td>
				<textarea id="plot" name="Plot" cols="50" rows="15" class="medium">%s</textarea></td><td>(e.g. story description)</td></tr>
			<tr id="tr_runtime"><td>Runtime:</td><td>
				<input id="runtime" name="Runtime" type="text" value="%s" class="small center"></input></td><td>(e.g. 90)</td></tr>
			<tr id="tr_year"><td>Year:</td><td>
				<input id="year" name="Year" type="text" maxlength="4" value="%s" class="small center"></td><td></input>(e.g. 2011)</td></tr>
			<tr id="tr_genres"><td>Genres:</td><td>
				<input id="genres" name="Genres" type="text" value="%s" class="medium"></input></td><td>(e.g. Action|Thriller)</td></tr>
			<tr id="tr_popularity"><td>Popularity:</td><td>
				<!--<input id="popularity" name="Popularity" type="text" value=""></input></td><td>(e.g. 9)-->				
				<select id="popularity" name="Popularity" class="small">	
				%s			
				</select>
				</td></tr>
				
			<tr id="tr_path"><td>Path:</td><td>
				<input class="medium requiredfield" id="path" name="Path" type="text" value="%s"></td><td></input>(e.g. /some/where/on/my/box/)</td></tr>
			<tr id="tr_filename"><td>Filename:</td><td>
				<input class="medium requiredfield"  id="filename" name="Filename" type="text" value="%s"></td><td></input>(e.g. my filename)</td></tr>
			<tr id="tr_extension" class="requiredlabel"><td>Extension:</td><td>
				<input class="small requiredfield"  id="extension" name="Extension" type="text" maxlength="4" value="%s"></td><td></input>(without leading . => e.g. mkv)</td></tr>		
			<tr id="tr_seen"><td>Seen</td><td>
				<input id="seen" name="Seen" type="checkbox" %s></td><td></input></td></tr>		
			<tr><td>
			<tr><td>
				<input type="submit" value="Save"></input>
			</td></tr>
		</form>
