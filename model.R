library(lme4)
library(data.table)

options("width" = 200)

data_dir <- "output"
out_dir <- "results"

get_anova_p <- function(delivery_df, col) {

  delivery_df_nm <- delivery_df[!is.na(delivery_df[[col]]), ]
  mixed_model_null <- glmer(form_valid_int ~ (1 | prenatal_provider)
                            , data = delivery_df_nm, family = binomial)
  mixed_model <- glmer(paste0("form_valid_int ~ ",
                              col,  " + (1 | prenatal_provider)")
                       , data = delivery_df_nm, family = binomial)
  anova_result <- anova(mixed_model, mixed_model_null)

  p <- anova_result[["Pr(>Chisq)"]][2]

  p
}

get_anova_p_patient <- function(delivery_df, col) {

  delivery_df_nm <- delivery_df[!is.na(delivery_df[[col]]), ]
  model_null <- glm(form_valid_int ~ 1
                    , data = delivery_df_nm, family = binomial)
  print(summary(model_null))
  model <- glm(paste0("form_valid_int ~ ", col)
               , data = delivery_df_nm, family = binomial)
  print(summary(model))
  anova_result <- anova(model, model_null)

  p <- anova_result[["Pr(>Chisq)"]][2]

  p
}

get_or <- function(delivery_df, col) {

  print(col)

  delivery_df_nm = delivery_df[!is.na(delivery_df[[col]]), ]
  mixed_model <- glmer(paste0("form_valid_int ~ ",
                              col,  " + (1 | prenatal_provider)")
                       , data = delivery_df_nm, family = binomial)

  est <- fixef(mixed_model)
  cc <- confint(mixed_model, parm = "beta_", method = "profile")
  # Wald, boot, profile
  logits_table <- cbind(est, cc)
  odds_ratio_table <- exp(logits_table)
  odds_ratio_table <- data.frame(odds_ratio_table)
  odds_ratio_table$factor <- rownames(odds_ratio_table)

  odds_ratio_table

}


get_or_covariates <- function(delivery_df, col, covariates) {

  print(col)

  delivery_df_nm <- delivery_df[!is.na(delivery_df[[col]]), ]
  for (covariate in covariates){
    delivery_df_nm <- delivery_df[!is.na(delivery_df[[covariate]]), ]
  }

  formula <- paste0("form_valid_int ~ ",
                    col, #" + ", paste(covariates, collapse = " + "),
                    " + (1 | prenatal_provider)")

  print(formula)

  mixed_model <- glmer(formula, data = delivery_df_nm, family = binomial)
  
  print("fitting CI")
  est <- fixef(mixed_model)
  cc <- confint(mixed_model, parm = "beta_",
                method = "boot", devtol = 1e-9) # Wald, boot, profile
  logits_table <- cbind(est, cc)
  odds_ratio_table <- exp(logits_table)
  odds_ratio_table <- data.frame(odds_ratio_table)
  odds_ratio_table$factor <- rownames(odds_ratio_table)

  odds_ratio_table[2, ]
}

# MAIN

self_peer <- c("self", "peer")[1]

# Read data
delivery_df <- read.csv(file = file.path(data_dir, paste0(self_peer, "_delivery_df.csv")))
# delivery_df <- delivery_df[delivery_df$Race != "White-Arab", ]
print(paste(nrow(delivery_df), "deliveries"))

# 4 - odds ratios on binary provider/interaction features (multivariable)
model_cols_bin <- c("Race_binary",  "Age_Range_binary",
                    "Specialty_binary", "Training_binary",
                    "Scope_binary", "Gender_Identity_binary",
                    "Religion_binary", "Race_same_binary",
                    "Ethnicity_same_binary")
# "Ethnicity_binary", "Age_difference_binary"

odds_ratio_list <-
  lapply(model_cols_bin, get_or_covariates, delivery_df = delivery_df,
         covariates = c("Race_binary", "Age_Range_binary",
                        "Gender_Identity_binary"))
odds_ratio_all <- rbindlist(odds_ratio_list, use.names = TRUE,
                            fill = FALSE, idcol = FALSE)
odds_ratio_all$OR_format <- paste0(round(odds_ratio_all$est, 2), " (",
                                   round(odds_ratio_all$X2.5.., 2), ", ",
                                   round(odds_ratio_all$X97.5.., 2), ")")
write.csv(odds_ratio_all,
          file = file.path(out_dir, 
                           paste0(self_peer, "_odds_ratios_multivariable.csv")),
          row.names = FALSE)

stop()

# 1 - anova on provider/combination features
model_cols_provider = c("Race",  "Age_Range", "Ethnicity", "Training", "Specialty", 
                        "Scope", "Gender_Identity", "Religion", "Race_same", 
                        "Ethnicity_same", "Age_difference") # "Comfort with Counseling Re: Permanent Contraception"
p_values_provider = sapply(model_cols, get_anova_p, delivery_df=delivery_df)
write.csv(p_values, file.path(out_dir, paste0(self_peer, "_anova_provider.csv")))

# 2 - anova on patient features
mom_demo_cols = c("mat_age_bin", "mom_ethn_backgr_f2", "marital_status_f_di2", "education_level_f", "race_upd2")
p_values_patient = sapply(mom_demo_cols, get_anova_p_patient, delivery_df=delivery_df)
write.csv(p_values, file.path(out_dir, "anova_patient.csv"))

# 3 - odds ratios on binary provider/interaction features (univariable)
model_cols_bin = c("Race_binary",  "Age_Range_binary", "Ethnicity_binary", "Specialty_binary",  "Training_binary",
                   "Scope_binary", "Gender_Identity_binary", "Religion_binary", "Race_same_binary", 
                   "Ethnicity_same_binary", "Age_difference_binary")
odds_ratio_list = lapply(model_cols_bin, get_or, delivery_df=delivery_df)
odds_ratio_all = rbindlist(odds_ratio_list, use.names=TRUE, fill=FALSE, idcol=FALSE)
odds_ratio_all$OR_format = paste0(round(odds_ratio_all$est, 2), " (", 
                                  round(odds_ratio_all$X2.5.., 2), ", ", 
                                  round(odds_ratio_all$X97.5.., 2), ")" )
write.csv(odds_ratio_all, file=file.path(out_dir, paste0(self_peer, "_odds_ratios_univariable.csv")), row.names=FALSE)   


stop()

# # Create binary feature columns
# for (feature_item in feature_list) {
#   col_name <- feature_item$col_name
#   print(table(delivery_df[[col_name]]))
#   col_name_new = paste0(feature_item$col_name, "_binary")
#   delivery_df[[col_name_new]] <-
#     feature_item$post[match(delivery_df[[col_name]], feature_item$pre)]
#   print(table(delivery_df[!duplicated(delivery_df["prenatal_provider"]), ]
#               [, c(col_name, col_name_new)]))
# }

# feature_list <- list(
#   list(col_name = "Race",
#        pre = c("Black", "Asian", "White"),
#        post = c(0, 0, 1)),
#   list(col_name = "Age_Range",
#        pre = c("20-30", "31-40", "41-50", "51-60", "60+"),
#        post = c(0, 0, 1, 1, 1)),
#   list(col_name = "Ethnicity",
#        pre = c("Hispanic", "Non-Hispanic"),
#        post = c(1, 0)),
#   list(col_name = "Training",
#        pre = c("attending", "fellow", "resident", "CNM", "NP/PA"),
#        post = c(1, 0, 0, 0, 0)),
#   list(col_name = "Specialty",
#        pre = c("MFM", "family medicine", "general OB-GYN"),
#        post = c(1, 0, 1)),
#   list(col_name = "Scope",
#        pre = c("OB only", "OB & GYN"),
#        post = c(0, 1)),
#   list(col_name = "Gender_Identity",
#        pre = c("Man", "Woman"),
#        post = c(0, 1)),
#   list(col_name = "Religion",
#        pre = c("atheist/agnostic", "catholic", "hindu",
#                "mormon", "jewish", "protestant"),
#        post = c(0, 1, 1, 1, 1)),
#   list(col_name = "Age_difference",
#        pre = c("younger", "same", "older"),
#        post = c(0, 0, 1)),
#   list(col_name = "Race_same",
#        pre = c(TRUE, FALSE),
#        post = c(0, 1)),
#   list(col_name = "Ethnicity_same",
#        pre = c(TRUE, FALSE),
#        post = c(0, 1))
#   # list(col_name = "Comfort with Counseling Re: Permanent Contraception",
#   #      pre = c("somewhat comfortable", "very comfortable"),
#   #      post = c(0, 1))
# )