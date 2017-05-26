var baseUrl = "http://192.168.0.146:8080";
var app_key = "tSAOAAgliQChZfKp7xSQ6uJmOtePqiL1";
var ixSearchUrl = "https://api.indix.com/v2/summary/products?app_key="+app_key;

function populateProducts (products) {
  $("#products").empty();
  products.forEach(function (product) {
    $("#products").append('<div class="col-6 col-lg-4">'+
      '<img style="height:200px; width: 160px;padding-left: 10px;" src="'+ product.imageUrl +'"/>'+
      '<p><span style="font-family: Arial; font-size: 16px;">'+ product.title +'</span><br>'+
      '<span style="font-family: Arial; font-size: 11px;">by '+product.brandName+'<br>'+
      '<span style="font-color: red; font-size: 13px;">from $'+ product.minSalePrice+' - '+ product.maxSalePrice +'</span><br>'+
      'Offers '+ product.offersCount + ' in '+ product.storesCount +' stores </p>'+
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

  var queryStr = '&countryCode=US&q=' + query;

  $.getJSON(ixSearchUrl + queryStr, null, function (resp) {
    console.log("Actual Seacrh ", resp.result);
    // populateProducts(resp.result.products, resp.result.count);
  });

}

function getBrands() {

}

function getStores () {

}

function getCategories() {

}

function getRefinedProducts(tags, query) {

  var queryStr = '&countryCode=US';

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
  getProducts(q);
  $.getJSON(baseUrl+"/api/tag", {q}, function (resp) {
    console.log("Tags: ", resp.tags);
    getRefinedProducts(resp.tags, resp.query);
    getBrands(resp.tags.brands);
    getStores(resp.tags.stores);
    getCategories(resp.tags.categories);
  })

}

$("#query").on('keyup', function (e) {
    if (e.keyCode == 13) {
        query();
    }
});
