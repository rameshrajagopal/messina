var baseUrl = "";
//var baseUrl = "";
var app_key = "tSAOAAgliQChZfKp7xSQ6uJmOtePqiL1";
var ixSearchUrl = "https://api.indix.com/v2.1/search?app_key="+app_key;

function populateProducts (products, count, query) {
  console.log(query)
  $("#products").empty();
  products.forEach(function (product) {
    const normalizedScore = ((product.searchScore + 100) * 0.5) + (query.split(" ").length/product.title.split(" ").length * 0.5)
    $("#products").append('<div class="col-6 col-lg-4">'+
      '<img style="height:200px; width: 160px;padding-left: 10px;" src="'+ product.image.url +'"/>'+
      '<p><span style="font-family: Arial; font-size: 16px;">'+ product.title +'</span><br>'+
      '<span style="font-family: Arial; font-size: 11px;">by '+product.brandName+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">category '+product.categoryNamePath+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">storeId: '+product.priceRange[0].storeId+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">searchScore: '+product.searchScore+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">normalizedScore: '+normalizedScore+'<br>'+
      '<span style="font-color: red; font-size: 13px;">from $'+ product.priceRange[0].salePrice+' - '+ product.priceRange[1].salePrice +'</span><br>'+
      'RatingCount '+ product.aggregatedRatings.ratingCount + ' RatingValue '+ product.aggregatedRatings.ratingValue +'</p>'+
      '</div>'
    );
  });
}

function populateProductsByType (type, products, query="") {
  var dom;
  switch (type) {
    case 'api':
      dom = $('#apiProducts'); break;
    case 'gatsby':
      dom = $('#gatsbyProducts'); break;
  }
  dom.empty();

  const popularity_weight = 0.4
  const relevance_weight = 0.3
  const saleprice_weight = 0.3

  const max_saleprice = products.reduce((acc, cur) => {
    const salePrice = cur.valuesForRanking ? parseInt(cur.valuesForRanking.salePrice) : 0
    return (acc >= salePrice) ? acc : salePrice
  }, 0)

  const max_relevance_score = products.reduce((acc, cur) => {
    const relevanceScore = cur.valuesForRanking ? parseInt(cur.valuesForRanking.relevanceScore) :0
    return (acc >= relevanceScore) ? acc : relevanceScore
  }, 0)

  const max_popularity_score = products.reduce((acc, cur) => {
    const popularityScore = cur.valuesForRanking ? parseInt(cur.valuesForRanking.popularityScore) : 0
    return (acc >= popularityScore) ? acc : popularityScore
  }, 0)

  const norm_pop_score = (max_popularity_score == 0 ? 0: (100.0)/(max_popularity_score)) * popularity_weight;
  const norm_rel_score = (max_relevance_score  == 0 ? 0: (100.0)/(max_relevance_score)) * relevance_weight;
  const norm_sale_price = (max_saleprice == 0 ? 0: (100.0)/(max_saleprice)) * saleprice_weight;



  products.forEach(function (product) {
    const normalizedScore  = (product.valuesForRanking) ?
       (product.valuesForRanking.salePrice * norm_sale_price) + (product.valuesForRanking.relevanceScore * norm_rel_score) + (product.valuesForRanking.popularityScore * norm_pop_score)
      : 0
    dom.append('<div class="col-lg-4">'+
      '<img style="height:200px; width: 160px;padding-left: 10px;" src="'+ product.image.url +'"/>'+
      '<p><span style="font-family: Arial; font-size: 16px;">'+ product.title +'</span><br>'+
      '<span style="font-family: Arial; font-size: 11px;">by '+product.brandName+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">mpid '+product.mpid+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">category '+product.categoryNamePath+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">storeId: '+product.priceRange[0].storeId+'<br>'+
      '<span style="font-family: Arial; font-size: 11px;">searchScore: '+product.searchScore+'<br>'+
      `${normalizedScore ? '<span style="font-family: Arial; font-size: 11px;">normalizedScore: '+normalizedScore+'<br>' : ''}`+
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
    console.log("Actual Search ", resp.result);
    populateProducts(resp.result.products, resp.result.count, query);
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
  var searchText = $('.btn-search').text();
  $('.btn-search').text('Searching..');

  var q = $("#query").val();
  var sortBy = $('select[name="sort_by"]').val();
  var storeIds = $('#store_id').val();

  if (!q) {
      alert("Please enter valid search term!!!");
      $('.btn-search').text('Search');
      return;
  }
  var params = {
    q: q,
    sort_by: sortBy,
    store_ids: storeIds.join(',')
  };
  console.log(params);

  $.getJSON(baseUrl+"/api/products", params,
    function (resp) {
      $('.btn-search').text(searchText);
      populateProductsByType('api', resp.api.products)
      populateProductsByType('gatsby', resp.gatsby.products, params.q)
   })
}

$("#query").on('keyup', function (e) {
    if (e.keyCode == 13) {
        query();
    }
});
