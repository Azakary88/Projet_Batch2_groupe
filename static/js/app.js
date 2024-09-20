function vote(button) {
    const projectId = button.getAttribute('data-project-id');
    fetch('/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: 'user', // tu peux changer dynamiquement ici
            project_id: projectId
        })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}

function purchaseProject(button) {
    const projectId = button.getAttribute('data-project-id');
    const username = prompt('Entrez votre nom d\'utilisateur:'); // Demande le nom d'utilisateur

    fetch('/buy_project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            project_id: projectId
        })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}

const username = document.getElementById('username').value;  // Exemple de récupération du nom
