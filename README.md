# PAT
PAT

`sam connect raspberrypi.local`

# Install Snips
```
sudo apt-get update
sudo apt-get install -y dirmngr

sudo bash -c 'echo "deb https://raspbian.snips.ai/$(lsb_release -cs) stable main" > /etc/apt/sources.list.d/snips.list'
# along with
sudo bash -c 'echo "deb https://raspbian.snips.ai/stretch stable main" >> /etc/apt/sources.list.d/snips.list'

sudo apt-key adv --keyserver pgp.mit.edu --recv-keys D4F50CDCA10A2849
sudo apt-get update
```

```
sudo apt-get install -y snips-platform-voice
sudo apt-get install -y snips-template snips-skill-server

```


## For installing Repseaker
```
git clone https://github.com/respeaker/seeed-voicecard
cd seeed-voicecard
sudo ./install.sh
sudo reboot
```

HDMI is device 0:1

Samson Meteor Mic is 1:0

edit `sudo nano /etc/asound.conf` to 
```
pcm.!default {
  type asym
   playback.pcm {
     type plug
     slave.pcm "hw:0,0"
   }
   capture.pcm {
     type plug
     slave.pcm "hw:1,0"
   }
}
```


```
sudo npm install -g snips-sam
sam devices
sam connect raspberrypi.local
sam init
```

```
sudo apt-get install vim
vim index.js
```

Insert into `index.js`:
```
var mqtt = require('mqtt');

var hostname = "mqtt://raspberrypi.local";
var client  = mqtt.connect(hostname);

client.on('connect', function () {
    console.log("[Snips Log] Connected to MQTT broker " + hostname);
    client.subscribe('hermes/#');
});

client.on('message', function (topic, message) {
    if (topic === "hermes/asr/startListening") {
        onListeningStateChanged(true);
    } else if (topic === "hermes/asr/stopListening") {
        onListeningStateChanged(false);
    } else if (topic.match(/hermes\/hotword\/.+\/detected/g) !== null) {
        onHotwordDetected()
    } else if (topic.match(/hermes\/intent\/.+/g) !== null) {
        onIntentDetected(JSON.parse(message));
    }
});

function onIntentDetected(intent) {
    console.log("[Snips Log] Intent detected: " + JSON.stringify(intent));
}

function onHotwordDetected() {
    console.log("[Snips Log] Hotword detected");
}

function onListeningStateChanged(listening) {
    console.log("[Snips Log] " + (listening ? "Start" : "Stop") + " listening");
}
```

install the following to get the right packages installed (`libblas-common` and `libatlas3-base`):
```
sudo apt-get install gdebi
```


Reinstall `node.js`:

