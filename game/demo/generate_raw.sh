#!/bin/bash
	echo '<odoo><data>'

while read raw
do
  ph=$(md5sum <<< "$RANDOM$raw" | tr 'a-z' '0-9' | tr -d '-')
  hh=$(md5sum <<< "$RANDOM$raw" | tr 'a-z' '0-9' | tr -d '-')
  dh=$(md5sum <<< "$RANDOM$raw" | tr 'a-z' '0-9' | tr -d '-')
  img=$(convert -size 100x100 -seed $ph plasma:fractal -quality 20% JPG:- | base64)

	echo '<record id="game.raw_'$raw'" model="game.raw">'
	echo '<field name="name">'$raw'</field>'
	echo '<field name="public_hash">'$ph'</field>'
	echo '<field name="hidden_hash">'$hh'</field>'
	echo '<field name="image">'"$img"'</field>'
	echo '<field name="construccio">'${dh:1:2}'</field>'
	echo '<field name="armesblanques">'${dh:3:2}'</field>'
	echo '<field name="armesfoc">'${dh:5:2}'</field>'
	echo '<field name="nutricio">'${dh:7:2}'</field>'
	echo '<field name="tecnologia">'${dh:9:2}'</field>'
	echo '<field name="medicina">'${dh:11:2}'</field>'
	echo '<field name="energia">'${dh:13:2}'</field>'
	echo '</record>'
done < raws
	echo '</data></odoo>'