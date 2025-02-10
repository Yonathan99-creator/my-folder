const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});

// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

// Cargar el estado de visibilidad del sidebar desde localStorage
if(localStorage.getItem('sidebarHidden') === 'true') {
	sidebar.classList.add('hide');
} else {
	sidebar.classList.remove('hide');
}

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
	
	// Guardar el estado del sidebar en localStorage
	if (sidebar.classList.contains('hide')) {
		localStorage.setItem('sidebarHidden', 'true');
	} else {
		localStorage.setItem('sidebarHidden', 'false');
	}
})

const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');
		if(searchForm.classList.contains('show')) {
			searchButtonIcon.classList.replace('bx-search', 'bx-x');
		} else {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
		}
	}
})

if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}

window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})

// Modo Oscuro
const switchMode = document.getElementById('switch-mode');

// Cargar el estado del modo oscuro desde localStorage
if(localStorage.getItem('darkMode') === 'true') {
	document.body.classList.add('dark');
	switchMode.checked = true;
} else {
	document.body.classList.remove('dark');
	switchMode.checked = false;
}

// Guardar el estado del modo oscuro cuando se cambie
switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
		localStorage.setItem('darkMode', 'true');
	} else {
		document.body.classList.remove('dark');
		localStorage.setItem('darkMode', 'false');
	}
});
