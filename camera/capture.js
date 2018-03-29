// vNext

const thisSessionId = getRandomName();
$('#sessionId').text(thisSessionId);

let BACKEND_BASE_URL = 'https://aa-backend.azurewebsites.net';

let videoElement = document.querySelector('#camera');
let videoSelect = document.querySelector('select#videoSource');
let selectors = [videoSelect];
let i = 0; // seconds counter for DEBUG

// Returns still bytes
function captureVideoFrame(video, format) {
  if (typeof video === 'string') {
    video = document.querySelector('#' + video);
    //console.log('[DEBUG] Capturing video from ', video);
  }

  format = format || 'jpeg';

  if (!video || (format !== 'png' && format !== 'jpeg')) {
    return false;
  }

  var canvas = document.createElement("canvas");

  //console.log('[DEBUG] hiddenCanvas is ', canvas);
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  var dataUri = canvas.toDataURL('image/' + format);
  var data = dataUri.split(',')[1];
  var mimeType = dataUri.split(';')[0].slice(5)

  var bytes = window.atob(data);
  var buf = new ArrayBuffer(bytes.length);
  var arr = new Uint8Array(buf);

  for (var i = 0; i < bytes.length; i++) {
    arr[i] = bytes.charCodeAt(i);
  }
  var blob = new Blob([arr], { type: mimeType });

  return { blob: blob, dataUri: dataUri, format: format, bytes: bytes, arr: arr };
}

// Capture a photo by fetching the current contents
// of the <video> element
function takePhoto() {
  var frame = captureVideoFrame('camera', 'jpeg');
  i++; // just for debug
  console.log(`Say cheese! - frames sent: ${i}`);
  const uploadUrl = BACKEND_BASE_URL;
  $.ajax({
    url: uploadUrl,
    method: 'POST',
    data: frame.arr,
    processData: false,
    contentType: 'application/octet-stream',
    headers: { "SESSIONID": thisSessionId },
    success: function (data, textStatus, xhr) {
      console.log(`${textStatus}. Got response: ${xhr.status} ${xhr.statusText}`);
      console.log(data);
    },
    fail: function (data) {
      console.log(data);
    }
  });
}

function gotDevices(deviceInfos) {
  // Handles being called several times to update labels. Preserve values.
  var values = selectors.map(function (select) {
    return select.value;
  });
  selectors.forEach(function (select) {
    while (select.firstChild) {
      select.removeChild(select.firstChild);
    }
  });
  for (var i = 0; i !== deviceInfos.length; ++i) {
    var deviceInfo = deviceInfos[i];
    var option = document.createElement('option');
    option.value = deviceInfo.deviceId;
    if (deviceInfo.kind === 'videoinput') {
      option.text = deviceInfo.label || 'camera ' + (videoSelect.length + 1);
      videoSelect.appendChild(option);
      console.log(deviceInfo);
    } else {
      //console.log('Some other kind of source/device: ', deviceInfo);
    }
  }
  selectors.forEach(function (select, selectorIndex) {
    if (Array.prototype.slice.call(select.childNodes).some(function (n) {
      return n.value === values[selectorIndex];
    })) {
      select.value = values[selectorIndex];
    }
  });
}

function gotStream(stream) {
  window.stream = stream; // make stream available to console
  videoElement.srcObject = stream;
  // Refresh button list in case labels have become available
  return navigator.mediaDevices.enumerateDevices();
}

function start() {
  if (window.stream) {
    window.stream.getTracks().forEach(function (track) {
      track.stop();
    });
  }
  var videoSource = videoSelect.value;
  var constraints = {
    video: { deviceId: videoSource ? { exact: videoSource } : undefined }
  };
  navigator.mediaDevices.getUserMedia(constraints).
    then(gotStream).then(gotDevices).catch(handleError);
}

function handleError(error) {
  console.log('navigator.getUserMedia error: ', error);
}


$(document).ready(() => {
  navigator.mediaDevices.enumerateDevices().then(gotDevices).catch(handleError);
  // Restart stream on new video source
  videoSelect.onchange = start;
  // Start stream
  start();

  let live = false;
  let loop;

  $('#startbutton').click((event) => {
    console.log('[DEBUG] live is ', live);
    if (live === false) {
      // Send frame to backend every 5 seconds
      loop = setInterval(takePhoto, 5000);
      console.log('[DEBUG] ON AIR!');
      $('#startbutton').text('ON AIR!');
      live = true;
    }
    else {
      clearInterval(loop);
      console.log('[DEBUG] Streaming stopped.');
      $('#startbutton').text('Start streaming');
      live = false;
    }
  });
});