document.getElementById('analyse').addEventListener('click', function(event) {
    try {
        const crashData = JSON.parse(document.getElementById('crashData').value);
        displayCrashReport(crashData);
    } catch (error) {
        document.getElementById('report').innerText = "Error: Failed to read JSON data: " + error;
    }
});

function displayCrashReport(data) {
    let reportHtml = `<h2>Crash informations</h2>`;

    reportHtml += `<p><strong>BeaconMC Version :</strong> ${data.beaconmc_version}</p>`;
    reportHtml += `<p><strong>OS :</strong> ${data.os_name}</p>`;
    reportHtml += `<p><strong>Python Version :</strong> ${data.python_version}</p>`;
    reportHtml += `<p><strong>Date :</strong> ${data.date}</p>`;
    reportHtml += `<p><strong>Total Plugins :</strong> ${data.total_plugin}</p>`;

    reportHtml += `<h3>Traceback :</h3><pre>${data.traceback_error}</pre>`;

    reportHtml += `<h2>Analyse & Suggestions</h2>`;
    reportHtml += analyzeCrash(data);

    document.getElementById('report').innerHTML = reportHtml;
}

function analyzeCrash(data) {
    let suggestions = "<ul>";

    if (parseFloat(data.python_version) < 3.8) {
        suggestions += "<li><strong>⚠️ Version de Python obsolète.</strong> Mettez à jour vers Python 3.8 ou supérieur.</li>";
    }

    if (data.os_name.toLowerCase().includes("windows")) {
        // soon
    }


    
    if (data.traceback_error.includes("FileNotFoundError")) {
        suggestions += "<li>❌ A file was not found by BeaconMC. Try to reinstall the project or running start.py.</li>";
    }

    if (data.traceback_error.includes("ModuleNotFoundError")) {
        suggestions += "<li>📦 A Python module is missing. Try running the project in the global environnement or installing in your specific environnement the project dependencies.</li>";
    }

    suggestions += "</ul>";
    return suggestions;
}
