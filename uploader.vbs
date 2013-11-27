url = "http://app.povelli.com/api/910e9096-4970-4f7e-b44c-2741f9351d76/pricebook-upload/"


set fso = createobject("scripting.filesystemobject")

while true

'wscript.echo "Checking..."

	set folder = fso.getfolder("C:\Users\Chris\AppData\Local\Tri-Xar Systems\JSon")

	set files = folder.files

	for each file in files

		if instr(file.name, "-bad") = 0 then

		wscript.echo "Uploading ", file.name, " | ", file.size, " ..."

		set f = fso.opentextfile(file.path, 1)
		content = f.readall
		f.close

		bnd = "---------------------------7d323f12e0740"

		data = "--" & bnd & vbcrlf
		data = data & "Content-Disposition: form-data; name=""file"";"
		data = data & " filename=""data.json""" & vbcrlf
		data = data & "Content-Type: application/json" & vbcrlf & vbcrlf
		data = data & content
		data = data & vbcrlf & "--" & bnd & "--"

		set http = createobject("winhttp.winhttprequest.5.1")
		http.open "POST", url, false
		http.setrequestheader "Content-Type", "multipart/form-data; boundary=" & bnd
		http.send data
		resp = http.responsetext

		if instr(resp, """success"": true") > 0 then
			wscript.echo "Done... Deleting file..."
			file.delete
		else
			file.move file.path & "-bad"
			wscript.echo resp
		end if
		
		end if

	next

	wscript.sleep(2000)

wend
