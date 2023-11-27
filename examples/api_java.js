var url = "http://127.0.0.1:14053/v2/1234/pose";
var http = new XMLHttpRequest();

function fetchPoseData() {
    http.open('POST', url, true);
    http.setRequestHeader('Content-Type', 'application/json');

    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {
            var poseData = JSON.parse(http.response);
            console.log(poseData);
        }
    }

    var requestData = JSON.stringify({ "name": "ue5_manny", "mode": "motion" });
    http.send(requestData);
}

// Call the function to fetch the pose data
fetchPoseData();

