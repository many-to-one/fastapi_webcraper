const category = document.body.dataset.category

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
    var date = document.getElementById('date').value;
    console.log('title', title);
    console.log('date:', date);
    console.log('filter', filter);

    window.location.href = `/visualization-test/${category}?search=${title}&filter_by=${filter}&date=${date}`;
}

function showVisTitle() {

    var title = document.getElementById('title').value;
    var filter = document.getElementById('filter').value;
    var date = document.getElementById('date').value;
    console.log('title', title);
    console.log('filter', filter);
    console.log('date', date);

    window.location.href = `/visualization-test/${category}?search=${title}&filter_by=${filter}&date=${date}`;
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
    console.log('selectedFilter', selectedFilter);
    let urlParam = new URLSearchParams(window.location.search)
    let searchParam = urlParam.get("search")
    let searchDate = urlParam.get("date")
    console.log("searchParam:", searchParam);
    console.log('category', category);

    window.location.href = `/visualization-test/${category}?search=${encodeURIComponent(searchParam)}&filter_by=${selectedFilter}&date=${searchDate}`;
});


document.addEventListener("DOMContentLoaded", function () {

    let urlParam = new URLSearchParams(window.location.search)
    let filterBy = urlParam.get("filter_by")
    let searchParam = urlParam.get("search")
    console.log('category', category);
    console.log('filterBy', filterBy);
    console.log('searchParam', searchParam);
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

