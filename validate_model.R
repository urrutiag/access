library(lme4)
library(data.table)
library(pROC)

options("width" = 200)

data_dir <- "output"
out_dir <- "results"


delivery_df <- read.csv(file = file.path(data_dir, "peer_delivery_df.csv"))
vars = c("Race_binary", "Age_Range_binary", "Gender_Identity_binary", "Specialty_binary", "Training_binary", "Scope_binary", "Religion_binary", "prenatal_provider", "Race_same_binary", "Ethnicity_same_binary", "Age_difference_binary")
print(table(delivery_df$site))
train_data <- delivery_df # delivery_df[delivery_df$site %in% c("UAB"), ]
print(train_data$prenatal_provider)
print(nrow(train_data))
print(summary(train_data[vars]))

# test_data <- delivery_df[delivery_df$site %in% c("UCSF", "MetroHealth"), ]
# test_data <- test_data[test_data$Race != "", ]
# print(nrow(test_data))

for( col in c("Race_binary", "Ethnicity_binary", "Age_Range_binary", "Gender_Identity_binary", "Scope_binary",  "prenatal_provider")){
    print(col)
    print(table(train_data[[col]]))
    # print(table(test_data[[col]]))
    train_data <- train_data[train_data[[col]] != "", ]
    # test_data <- test_data[test_data[[col]] != "", ]
}
# print(nrow(test_data))
# print(nrow(train_data))
# mixed_model <- glmer(
#     "form_valid_int ~ Race_binary + Age_Range_binary + Gender_Identity_binary + Scope_binary + (1 | prenatal_provider)"
#     , data = train_data, family = binomial)
# mixed_model <- glm(
#     "form_valid_int ~ mat_age_bin + mom_ethn_backgr_f2 + marital_status_f_di2 + education_level_f + race_upd2"
#     , data = train_data, family = binomial)
# mixed_model <- glmer(
#     "form_valid_int ~ Race_binary + Ethnicity_binary + Age_Range_binary + Gender_Identity_binary + Scope_binary + 
#     Race_same_binary + Ethnicity_same_binary + Age_difference_binary +
#     (1 | prenatal_provider)"
#     , data = train_data, family = binomial)
# mom_demo_cols = c("mat_age_bin", "mom_ethn_backgr_f2", "marital_status_f_di2", "education_level_f", "race_upd2")
mixed_model <- glmer(
    "form_valid_int ~ 
    Race_same_binary + Ethnicity_same_binary + Age_difference_binary +
    (1 | prenatal_provider)"
    , data = train_data, family = binomial)
print(mixed_model)
print(summary(mixed_model))

train_data$prediction = predict(mixed_model, newdata = train_data, allow.new.levels = TRUE, type="response")
# print(head(test_data))
print(mean(train_data[train_data$form_valid_int == 1, ]$prediction))
print(mean(train_data[train_data$form_valid_int == 0, ]$prediction))
print(roc(train_data$form_valid_int, train_data$prediction))