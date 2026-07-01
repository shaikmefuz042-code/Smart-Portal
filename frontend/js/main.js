<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Faculty Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f7fa; color: #333; }
        h1, h2 { color: #2c3e50; }
        .section { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background: #3498db; color: white; }
        button { background: #3498db; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #2980b9; }
        select, input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
        #logout { position: absolute; top: 20px; right: 20px; }
        #attendance-results { display: none; }
    </style>
</head>
<body>
    <button id="logout">Logout</button>
    <h1>Faculty Dashboard</h1>
    <div class="section" id="faculty-info">
        <h2>Your Credentials</h2>
        <p><strong>Name:</strong> <span id="name"></span></p>
        <p><strong>Faculty ID:</strong> <span id="id"></span></p>
        <p><strong>Email:</strong> <span id="email"></span></p>
    </div>
    <div class="section">
        <h2>Check Attendance</h2>
        <select id="year-select">
            <option value="">Select Year</option>
            <option value="1st Year">1st Year</option>
            <option value="2nd Year">2nd Year</option>
            <option value="3rd Year">3rd Year</option>
            <option value="4th Year">4th Year</option>
        </select>
        <select id="branch-select" disabled>
            <option value="">Select Branch</option>
            <option value="CSBS">CSBS</option>
            <option value="SIML">SIML</option>
            <option value="CS">CS</option>
            <option value="DS">DS</option>
            <option value="IOT">IOT</option>
        </select>
        <select id="student-select" disabled>
            <option value="">Select Student</option>
        </select>
        <button id="check-btn" disabled>Check Attendance</button>
        <div id="attendance-results">
            <h3>Attendance Records for <span id="student-display"></span></h3>
            <table id="attendance-table">
                <thead><tr><th>Date</th><th>Status</th></tr></thead>
                <tbody id="attendance-body"></tbody>
            </table>
            <p id="no-records" style="display: none; color: red;">No attendance records found for this student.</p>
        </div>
    </div>
    <div class="section">
        <h2>Mark Attendance</h2>
        <button id="start-btn">Start Webcam</button>
        <video id="video" autoplay style="display:block; border:1px solid #ddd;"></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <table id="marked-table">
            <thead><tr><th>S.No</th><th>Roll</th><th>Name</th><th>Status</th></tr></thead>
            <tbody id="marked-body"></tbody>
        </table>
    </div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const facultyId = urlParams.get('id');
        document.getElementById('logout').addEventListener('click', () => window.location.href = '/');
        fetch(`/faculty/data/${facultyId}`).then(r => r.json()).then(data => {
            document.getElementById('name').textContent = data.name || 'N/A';
            document.getElementById('id').textContent = data.faculty_id || 'N/A';
            document.getElementById('email').textContent = data.email || 'N/A';
        });
        const yearSelect = document.getElementById('year-select');
        const branchSelect = document.getElementById('branch-select');
        const studentSelect = document.getElementById('student-select');
        const checkBtn = document.getElementById('check-btn');
        yearSelect.addEventListener('change', () => {
            if (yearSelect.value) {
                branchSelect.disabled = false;
                studentSelect.disabled = true;
                checkBtn.disabled = true;
            } else {
                branchSelect.disabled = true;
                studentSelect.disabled = true;
                checkBtn.disabled = true;
            }
        });
        branchSelect.addEventListener('change', () => {
            const year = yearSelect.value;
            const branch = branchSelect.value;
            if (year && branch) {
                fetch(`/students/${year}/${branch}`).then(r => r.json()).then(students => {
                    studentSelect.innerHTML = '<option value="">Select Student</option>';
                    students.forEach(student => {
                        const option = document.createElement('option');
                        option.value = student.roll_no;
                        option.textContent = `${student.roll_no} - ${student.name}`;
                        studentSelect.appendChild(option);
                    });
                    studentSelect.disabled = false;
                    checkBtn.disabled = false;
                });
            } else {
                student