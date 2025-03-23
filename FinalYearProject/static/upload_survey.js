document.getElementById("surveyForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const surveyLink = document.getElementById("survey_link").value;
    const className = document.getElementById("class_name").value;

    const response = await fetch('/upload_survey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ survey_link: surveyLink, class_name: className })
    });

    const result = await response.json();
    alert(result.message);
});
