#!/bin/bash
for i in `ls /tmp/SL`; do
  echo $i
  rm -rf /tmp/SL/$i
  cp -r /var/lib/sharelatex/data/compiles/${i} /tmp
  cd /tmp
  cd ${i}
  if [ -f "config.sh" ]; then
  	egrep -e ENteacherActivity=[0-9]+ -e ENstudentActivity=[0-9]+ -e FRteacherActivity=[0-9]+ -e FRstudentActivity=[0-9]+ config.sh > safe.sh
  	source safe.sh
  	if [[ -n "$ENteacherActivity" ]]; then
  		#english teacher version
		sed 's/\international\(true\|false\)/\internationaltrue/' -i config.tex
		sed 's/\answer\(true\|false\)/\answertrue/' -i config.tex
  		xelatex --jobname=ENteacher CM.tex
  		php /SL/upload.php $ENteacherActivity ./ENteacher.pdf
  	fi
  	if [[ -n "$ENstudentActivity" ]]; then
  		#english student version
		sed 's/\international\(true\|false\)/\internationaltrue/' -i config.tex
		sed 's/\answer\(true\|false\)/\answerfalse/' -i config.tex
  		xelatex --jobname=ENstudent CM.tex
                if [[ -n "$multipage" ]]; then
                        pdfjam --nup 2x2 --frame true --noautoscale false --delta "0.2cm 0.3cm" --landscape --scale 0.95 ENstudent.pdf --outfile 2x2.pdf
                        mv 2x2.pdf ENstudent.pdf
                fi
  		php /SL/upload.php $ENstudentActivity ./ENstudent.pdf
  	fi
  	if [[ -n "$FRteacherActivity" ]]; then
  		#french teacher version
		sed 's/\international\(true\|false\)/\internationalfalse/' -i config.tex
		sed 's/\answer\(true\|false\)/\answertrue/' -i config.tex
  		xelatex --jobname=FRteacher CM.tex
  		php /SL/upload.php $FRteacherActivity ./FRteacher.pdf
 	fi
  	if [[ -n "$FRstudentActivity" ]]; then
		#english teacher version
		sed 's/\international\(true\|false\)/\internationalfalse/' -i config.tex
		sed 's/\answer\(true\|false\)/\answerfalse/' -i config.tex
  		xelatex --jobname=FRstudent CM.tex
		if [[ -n "$multipage" ]]; then
			pdfjam --nup 2x2 --frame true --noautoscale false --delta "0.2cm 0.3cm" --landscape --scale 0.95 FRstudent.pdf --outfile 2x2.pdf
 			mv 2x2.pdf FRstudent.pdf
 		fi
		php /SL/upload.php $FRstudentActivity ./FRstudent.pdf 
  	fi
  fi
  rm -rf /tmp/$i 
done
