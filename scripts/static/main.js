var baseUrl = "http://192.168.0.152:8080";
//var baseUrl = "";
var app_key = "tSAOAAgliQChZfKp7xSQ6uJmOtePqiL1";
var ixSearchUrl = "https://api.indix.com/v2.1/search?app_key="+app_key;

function populateProducts (products) {
  $("#products").empty();
  products.forEach(function (product) {
    $("#products").append('<div class="col-6 col-lg-4">'+
      '<img style="height:200px; width: 160px;padding-left: 10px;" src="'+ product.image.url +'"/>'+
      '<p><span style="font-family: Arial; font-size: 16px;">'+ product.title +'</span><br>'+
      '<span style="font-family: Arial; font-size: 11px;">by '+product.brandName+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">category '+product.categoryNamePath+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">searchScore: '+product.searchScore+'<br>'+
      '<span style="font-color: red; font-size: 13px;">from $'+ product.priceRange[0].salePrice+' - '+ product.priceRange[1].salePrice +'</span><br>'+
      'RatingCount '+ product.aggregatedRatings.ratingCount + ' RatingValue '+ product.aggregatedRatings.ratingValue +'</p>'+
      '</div>'
    );
  });
}

function populateStatus (query, count, tags) {
  $("#sidebar").empty();
  $("#sidebar").append(
    '<p> Matched '+ count +'<br><br>'+
    'Refined Query:'+ query.replace(/\&/g, '<br>&nbsp;') +
    '</p><br><br>'
  );

  // Dumping the tags from /api/tags
  $('#sidebar').append('<pre>'+
    JSON.stringify(tags) +
    '</pre>'
  );
}


function getProducts(tags, query) {

  var queryStr = '&countryCode=IN&q=' + query;

  $.getJSON(ixSearchUrl + queryStr, null, function (resp) {
    console.log("Actual Seacrh ", resp.result)  ;
    populateProducts(resp.result.products, resp.result.count);
  });

}

function getBrands() {

}

function getStores () {

}

function getCategories() {

}

function getRefinedProducts(tags, query) {

  var queryStr = '&countryCode=IN&pageSize=20';

  if (query)
    queryStr += ("&q=" + query);

  tags.brands.forEach(function (brand) {
    queryStr += brand.matches.map(function (brandId) {
      return "&brandId=" + brandId;
    }).join('');
  });

  tags.stores.forEach(function (store) {
    queryStr += store.matches.map(function (storeId) {
      return "&storeId=" + storeId;
    }).join('');
  });

  tags.categories.forEach(function (categ) {
    queryStr += categ.matches.map(function (categId) {
      return "&categoryId=" + categId;
    }).join('');
  });

  $.getJSON(ixSearchUrl + queryStr, null, function (resp) {
    console.log("products: ", resp);
    populateProducts(resp.result.products, resp.result.count);
    populateStatus(queryStr, resp.result.count, tags);
  });
}


function query () {
  var q = $("#query").val();
  var sortBy = $('select[name="sort_by"]').val();

  console.log(q)
  //getProducts(q);
  var searchText = $('.btn-search').text();
  $('.btn-search').text('Searching..');
  $.getJSON(baseUrl+"/api/products",
    {
      q: q,
      sort_by: sortBy
    },
    function (resp) {
      $('.btn-search').text(searchText);
      populateProducts(resp.products, resp.count)
  //    getRefinedProducts(resp);
  //    getBrands(resp.tags.brands);
  //    getStores(resp.tags.stores);
  //    getCategories(resp.tags.categories);
    })

}

$("#query").on('keyup', function (e) {
    if (e.keyCode == 13) {
        query();
    }
});
