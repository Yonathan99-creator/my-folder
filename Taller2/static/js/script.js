document.addEventListener("DOMContentLoaded", function () {
    const listItems = document.querySelectorAll(".lista");

    listItems.forEach((item) => {
        const listButton = item.querySelector(".lista_int");
        const listShow = item.querySelector(".lista_most");

        listButton.addEventListener("click", () => {
            item.classList.toggle("active");
        });
    });

    const cloud = document.getElementById("cloud");
    const barraLateral = document.querySelector(".barra-lateral");
    const spans = document.querySelectorAll("span");
    const palanca = document.querySelector(".switch");
    const circulo = document.querySelector(".circulo");
    const menu = document.querySelector(".menu");
    const main = document.querySelector("main");
    const chevronIcon = document.querySelector(".chevron-icon");
    const listaInt = document.querySelector(".lista_int");
    const search = document.querySelector('.input-group input'),
    table_rows = document.querySelectorAll('tbody tr'),
    table_headings = document.querySelectorAll('thead th');

// 1. Menu desplegable en el navbar   

    listaInt.addEventListener("click", () => {
        chevronIcon.style.transition = "transform 0.5s ease";
        chevronIcon.style.transform =
            chevronIcon.style.transform === "rotate(90deg)" ? "rotate(0deg)" : "rotate(90deg)";
    });

// 2. Barra Lateral    

    menu.addEventListener("click", () => {
        barraLateral.classList.toggle("max-barra-lateral");
        if (barraLateral.classList.contains("max-barra-lateral")) {
            menu.children[0].style.display = "none";
            menu.children[1].style.display = "block";
        } else {
            menu.children[0].style.display = "block";
            menu.children[1].style.display = "none";
        }
        if (window.innerWidth <= 320) {
            barraLateral.classList.toggle("mini-barra-lateral");
            main.classList.toggle("min-main");
            spans.forEach((span) => {
                span.classList.toggle("oculto");
            });
        }
    });

    cloud.addEventListener("click", () => {
        cloud.style.transition = "transform 0.5s ease";
        cloud.style.transform =
        cloud.style.transform === "rotate(180deg)" ? "rotate(0deg)" : "rotate(180deg)";
        barraLateral.classList.toggle("mini-barra-lateral");
        main.classList.toggle("min-main");
        spans.forEach((span) => {
            span.classList.toggle("oculto");
        });
    });

// 3. Modo obscuro    

    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add("dark-mode");
        circulo.classList.add("prendido");
    }

    palanca.addEventListener("click", () => {
        let body = document.body;
        body.classList.toggle("dark-mode");
        circulo.classList.toggle("prendido");

        const darkModeEnabled = body.classList.contains("dark-mode");
        localStorage.setItem('darkMode', darkModeEnabled);
    });   

// 4. Busqueda de un dato especifico

search.addEventListener('input', searchTable);

function searchTable() {
    table_rows.forEach((row, i) => {
        let table_data = row.textContent.toLowerCase(),
            search_data = search.value.toLowerCase();

        row.classList.toggle('hide', table_data.indexOf(search_data) < 0);
        row.style.setProperty('--delay', i / 25 + 's');
    })

    document.querySelectorAll('tbody tr:not(.hide)').forEach((visible_row, i) => {
        visible_row.style.backgroundColor = (i % 2 == 0) ? 'transparent' : '#0000000b';
    });
}

// 5. Ordenar los datos de la tabla

table_headings.forEach((head, i) => {
    let sort_asc = true;
    head.onclick = () => {
        table_headings.forEach(head => head.classList.remove('active'));
        head.classList.add('active');

        document.querySelectorAll('td').forEach(td => td.classList.remove('active'));
        table_rows.forEach(row => {
            row.querySelectorAll('td')[i].classList.add('active');
        })

        head.classList.toggle('asc', sort_asc);
        sort_asc = head.classList.contains('asc') ? false : true;

        sortTable(i, sort_asc);
    }
})


function sortTable(column, sort_asc) {
    [...table_rows].sort((a, b) => {
        let first_row = a.querySelectorAll('td')[column].textContent.toLowerCase(),
            second_row = b.querySelectorAll('td')[column].textContent.toLowerCase();

        return sort_asc ? (first_row < second_row ? 1 : -1) : (first_row < second_row ? -1 : 1);
    })
        .map(sorted_row => document.querySelector('tbody').appendChild(sorted_row));
}

// 6. Cerrar alertas

    const closeAlertBtn = document.getElementById('closeAlert');
    const alertBox = document.querySelector('.alert');

    closeAlertBtn.addEventListener('click', function() {
        alertBox.style.display = 'none';
    });

// 7. Tablas de compra y venta

    const tableBody = document.querySelector('.table3 .table__body');

    function updateTableHeight() {
        const currentHeight = tableBody.scrollHeight; 
        const maxHeight = window.innerHeight * 0.7;

        if (currentHeight <= maxHeight) {
            tableBody.style.height = currentHeight + 'px';
        } else {
            tableBody.style.height = maxHeight + 'px';
        }
    }

    updateTableHeight();

    const addButton = document.getElementById('addButton');
    addButton.addEventListener('click', function() {
        const newRow = document.createElement('tr');
        tableBody.appendChild(newRow);

        updateTableHeight();
    });    
}); 