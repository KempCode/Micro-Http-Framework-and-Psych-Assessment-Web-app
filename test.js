var domTreeLinks = document.getElementsByTagName('a');

var anchorCounter = 0
for(var i = 0; i < domTreeLinks.length; i++){
    if(domTreeLinks[i].hasAttribute("href")){
        anchorCounter += 1;
    }
}

document.write("Number of dom tree links " + domTreeLinks.length.toString() + "Number of anchors "+ anchorCounter)
