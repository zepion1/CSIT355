async function loadClasses() {
    try {
        const response = await fetch('/view_classes');
        if (!response.ok) {
            throw new Error('Failed to fetch classes');
        }
        const classes = await response.json();

        const tableBody = document.getElementById('classes-table-body');
        tableBody.innerHTML = '';
        classes.forEach(course => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${course.course_id}</td>
                <td>${course.course}</td>
                <td>${course.pname}</td>
                <td>${course.capacity}</td>
                <td>${course.credits}</td>
                <td>
                    <form method="POST" action="/enroll">
                        <input type="hidden" name="course_id" value="${course.course_id}">
                        <button type="submit" class="enroll-button">Enroll</button>
                    </form>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error(error);
        alert('Error loading classes. Please try again.');
    }
}
document.addEventListener('DOMContentLoaded', loadClasses);