<?php
 $server="moodle1.u-bordeaux.fr";
 $token="ae4ef8c9296c66c8de70416dc28fcc64";
  if ($argc < 3 ){
    exit( "Usage: ".$argv[0]." <rid> <files>\n" );
  }
  $target_url = "https://".$server."/webservice/rest/server.php";   

      $fname         = $argv[2];
  $rid         = $argv[1];    

      $file_name_with_full_path = realpath($fname);   
      $cfile = new CURLFile($file_name_with_full_path);

      $post = array (
                'wstoken'   => $token,    
                'wsfunction'   => 'local_uploadpdf_up',   
                'moodlewsrestformat'   => 'json',
                'rid' => $rid,
    'upload_file' => $cfile
      );    

      $ch = curl_init();
      curl_setopt($ch, CURLOPT_URL, $target_url);
      curl_setopt($ch, CURLOPT_POST, 1);
      curl_setopt($ch, CURLOPT_HEADER, 0);
      curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
      curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");   
      curl_setopt($ch, CURLOPT_HTTPHEADER,array('User-Agent: Opera/9.80 (Windows NT 6.2; Win64; x64) Presto/2.12.388 Version/12.15','Referer: http://localhost','Content-Type: multipart/form-data'));
      curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);   
      curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);  
      curl_setopt($ch, CURLOPT_TIMEOUT, 10);
      curl_setopt($ch, CURLOPT_POSTFIELDS, $post);


      $result = curl_exec ($ch);

      if ($result === FALSE) {
          echo "Error sending " . $fname .  " " . curl_error($ch) . "\n";
      }else{
          echo  "Result: " . $result;
      }
  curl_close($ch); 
