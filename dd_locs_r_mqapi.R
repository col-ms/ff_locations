library(httr)
library(jsonlite)
library(dplyr)

bb_set <- c("24.00,-85.00,49.00,-125.00",
            "24.00,-85.00,49.50,-80.00",
            "24.00,-80.00,49.50,-76.25",
            "24.00,-76.25,49.50,-73.00",
            "24.00,-73.00,49.50,-69.50",
            "24.00,-69.50,49.50,-66.00",
            "50.70,-169.30,71.70,-140.00",
            "15.00,-179.00,29.00,-154.00")

dd_df <- tibble()

for(bb in bb_set){
  params <- list(key = '4XWxa4hnzMheytBGszWEWqoBPwzLk4wI',
                 boundingBox = bb,
                 units = 'm',
                 maxMatches = '4000',
                 hostedData = 'mqap.33454_DunkinDonuts',
                 outFormat = 'json',
                 ambiguities = 'ignore')
  
  get_result <- GET(url = 'http://www.mapquestapi.com/search/v2/rectangle?',
                    query = params)
  
  http_type(get_result)
  
  pview <- fromJSON(content(get_result, as = "text"),
                    simplifyDataFrame = TRUE)$searchResults$fields
  
  selected_cols <- pview %>%
    select(recordid, address, address2, city,
           state, postal, county, country,
           phonenumber, lat, lng, sun_hours, mon_hours,
           tue_hours, wed_hours, thu_hours, fri_hours,
           sat_hours, sitetype, pos_type, co_brander_cd,
           operation_status_cd, dma_cd, close_reason_cd,
           otg_menu_opt, combostore, beverageonly,
           curbside, drivein, wireless, mobile,
           mobile_bypass_lane, dunkincardenabled,
           loyalty, adv_ord, high_vol_brewer,
           next_gen_store, catering_flag, walkin_flag,
           kosher, dt_auto_fire, turbooven, k_cup,
           almond, tender_agnostic_enabled)
  
  dd_df <- rbind(dd_df, selected_cols)
}
