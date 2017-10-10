REM curl -H "Content-type: application/octet-stream" -H "SESSIONID: blabla1" -X POST localhost:5555 --data-binary @img/multiple-faces.jpg
REM curl -H "Content-type: application/octet-stream" -H "SESSIONID: blabla2" -X POST localhost:5555 --data-binary @img/detection-1-thumbnail.jpg
REM curl -H "Content-type: application/octet-stream" -H "SESSIONID: blabla2" -X POST audience-analysis.azurewebsites.net --data-binary @img/detection-1-thumbnail.jpg

curl -H "Content-type: application/octet-stream" -H "SESSIONID: blabla1" -X POST localhost:5555 --data-binary @img/download.jfif