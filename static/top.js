let stream = null;
let mybutton = document.getElementById("myBtn");
window.onscroll = function () { scrollFunction() };

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
function uploadImage() {
    const formData = new FormData(document.getElementById('uploadForm'));
    fetch('/predict', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            // แสดงภาพผลลัพธ์
            const resultImage = document.getElementById('resultImage');
            resultImage.src = 'data:image/jpeg;base64,' + data.result_image;
            resultImage.style.display = 'block'; // ทำให้รูปภาพแสดง

            // แสดงการคาดการณ์
            const predictionsDiv = document.getElementById('predictions');
            predictionsDiv.innerHTML = ''; // ล้างข้อความเก่า
            data.predictions.forEach(prediction => {
                predictionsDiv.innerHTML += `
                <p>Class: ${prediction.class_id} <br>
                Coordinates: ${prediction.coordinates} <br>
                Confidence: ${prediction.confidence}</p>
            `;
            });

            // ทำให้ทั้งรูปภาพและการคำนวณปรากฏพร้อมกัน
            document.getElementById('result').style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}


