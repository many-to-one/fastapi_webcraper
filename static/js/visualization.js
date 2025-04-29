function showMenu() {
    const subContent = document.getElementById('menu');

    if (subContent.style.display === "none" || subContent.style.display === "") {
        subContent.style.display = "block";
    } else {
        subContent.style.display = "none";
    }
}

function showVis() {

    var title = document.getElementById('title').value;
    var category = document.getElementById("selectedCat").value;
    var filter = document.getElementById('filter').value;
    console.log('title', title);
    console.log('category:', category);
    console.log('filter', filter);

    window.location.href = `/visualization/${category}?search=${title}&filter_by=${filter}`;
}

function showCat(number) {
    const subContent = document.getElementById(`accordion-content-${number}`);

    if (subContent.style.display === "none" || subContent.style.display === "") {
        subContent.style.display = "block";
    } else {
        subContent.style.display = "none";
    }

}

// function setSubCat(category, number) {
//     console.log('selected category:', category);
//     document.getElementById("selectedCat").value = category;
//     var selected_category = document.getElementById('selected_category');
//     selected_category.innerHTML = category;
//     showCat(number);
//     showMenu();
//     showVis();
// }


// DINAMICALY FILTER OFFERS BY CHANGING SELECTED FILTER OPTION
document.getElementById("filter").addEventListener("change", function () {
    let selectedFilter = this.value; // Get selected filter value
    let date = document.getElementById('date').value;

    console.log('selectedFilter', selectedFilter)

    // Get current URL and extract category filename
    let currentUrl = new URL(window.location.href);
    let match = currentUrl.pathname.match(/visualization\/(.*?)\.xlsx/); // Extract category from URL

    if (match) {
        let categoryName = match[1]; // Get the category name

        // Preserve search parameter if it exists
        let searchParam = currentUrl.searchParams.get("search") || ""; // Keep existing search value

        // Redirect with updated filter and search query
        window.location.href = `/visualization/${categoryName}?search=${encodeURIComponent(searchParam)}&filter_by=${selectedFilter}&date=${date}`;
    }
});


// DINAMICALY FILTER OFFERS BY CHANGING SELECTED DAY OPTION
document.getElementById("date").addEventListener("change", function () {
    let selectedFilter = this.value; // Get selected filter value
    let filter = document.getElementById('date').value;

    // Get current URL and extract category filename
    let currentUrl = new URL(window.location.href);
    let match = currentUrl.pathname.match(/visualization\/(.*?)\.xlsx/); // Extract category from URL

    if (match) {
        let categoryName = match[1]; // Get the category name

        // Preserve search parameter if it exists
        let searchParam = currentUrl.searchParams.get("search") || ""; // Keep existing search value

        // Redirect with updated filter and search query
        window.location.href = `/visualization/${categoryName}?search=${encodeURIComponent(searchParam)}&filter_by=${filter}&date=${selectedFilter}`;
    }
});


document.addEventListener("DOMContentLoaded", function () {
    let urlParam = new URLSearchParams(window.location.search)
    let filterBy = urlParam.get("filter_by")
    let filterName;
    if (filterBy) {
        let selOpt = document.getElementById("sel_opt");
        if (filterBy === "reviews") {
            filterName = "Popularnośc";
        } else if (filterBy === "price") {
            filterName = "Cena";
        } else if (filterBy === "rating") {
            filterName = "Ocena";
        }
        selOpt.textContent = filterName; // Update displayed text
        selOpt.value = filterBy; // Update value
    }
})

