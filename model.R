library(lme4)
library(data.table)

options("width" = 200)

data_dir <- "output"
out_dir <- "results"

get_anova_p <- function(delivery_df, col) {

  delivery_df_nm <- delivery_df[!is.na(delivery_df[[col]]), ]
  mixed_model_null <- glmer(form_valid_int ~ (1 | prenatal_provider)
                            , data = delivery_df_nm, family = binomial)
  print(summary(mixed_model_null))
  mixed_model <- glmer(paste0("form_valid_int ~ ",
                              col,  " + (1 | prenatal_provider)")
                       , data = delivery_df_nm, family = binomial)
  
  print(summary(mixed_model))
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
  anova_result <- anova(model, test="Chisq")
  
  # print(anova_result)
  p <- anova_result[["Pr(>Chi)"]][2]
  # print(p)
  
  p
}

get_or <- function(delivery_df, col) {

  print(col)

  delivery_df_nm = delivery_df[!is.na(delivery_df[[col]]), ]
  mixed_model <- glmer(paste0("form_valid_int ~ ",
                              col,  " + (1 | prenatal_provider)")
                       , data = delivery_df_nm, family = binomial)

  est <- fixef(mixed_model)
  cc <- confint(mixed_model, parm = "beta_", method = "Wald")
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
                    col, " + ", paste(covariates, collapse = " + "),
                    " + (1 | prenatal_provider)")

  print(formula)

  mixed_model <- glmer(formula, data = delivery_df_nm, family = binomial)
  
  print("fitting CI")
  est <- fixef(mixed_model)
  cc <- confint(mixed_model, parm = "beta_",
                method = "Wald") # Wald, boot, profile , devtol = 1e-6
  logits_table <- cbind(est, cc)
  odds_ratio_table <- exp(logits_table)
  odds_ratio_table <- data.frame(odds_ratio_table)
  odds_ratio_table$factor <- rownames(odds_ratio_table)

  print(odds_ratio_table)

  odds_ratio_table[2, ]
}

# MAIN

self_peer <- c("self", "peer")[1]

# Read data
delivery_df <- read.csv(file = file.path(data_dir, paste0(self_peer, "_delivery_df.csv")))
# delivery_df <- delivery_df[delivery_df$Race != "White-Arab", ]
print(paste(nrow(delivery_df), "deliveries"))

# # 4 - odds ratios on binary provider/interaction features (multivariable)
# model_cols_bin_profile <- c("Race_binary",  "Age_Range_binary", "Gender_Identity_binary",
#                     "Specialty_binary", "Training_binary",
#                     "Scope_binary",
#                     "Religion_binary")
# model_cols_bin_wald <- c("Ethnicity_binary", "Age_difference_binary", "Race_same_binary",
#                     "Ethnicity_same_binary")
# model_cols_bin_wald_self <- c("Race_binary",  "Age_Range_binary", "Gender_Identity_binary",
#                     "Specialty_binary", "Training_binary",
#                     "Scope_binary",
#                     "Religion_binary", "Ethnicity_binary", "Age_difference_binary", "Race_same_binary",
#                     "Ethnicity_same_binary")
# model_cols_bin <- model_cols_bin_wald_self
# odds_ratio_list <-
#   lapply(model_cols_bin, get_or_covariates, delivery_df = delivery_df,
#          covariates = c("Race_binary", "Age_Range_binary",
#                         "Gender_Identity_binary"))
# odds_ratio_all <- rbindlist(odds_ratio_list, use.names = TRUE,
#                             fill = FALSE, idcol = FALSE)
# odds_ratio_all$OR_format <- paste0(round(odds_ratio_all$est, 2), " (",
#                                    round(odds_ratio_all$X2.5.., 2), ", ",
#                                    round(odds_ratio_all$X97.5.., 2), ")")
# write.csv(odds_ratio_all,
#           file = file.path(out_dir, 
#                            paste0(self_peer, "_odds_ratios_multivariable.csv")),
#           row.names = FALSE)
# stop()

# # 1 - anova on provider/combination features
# model_cols_provider = c("Race",  "Age_Range", "Ethnicity", "Training", "Specialty", 
#                         "Scope", "Gender_Identity", "Religion", "Race_same", 
#                         "Ethnicity_same", "Age_difference") # "Comfort with Counseling Re: Permanent Contraception"
# p_values_provider = sapply(model_cols_provider, get_anova_p, delivery_df=delivery_df)
# write.csv(p_values_provider, file.path(out_dir, paste0(self_peer, "_anova_provider.csv")))

# # 2 - anova on patient features
# mom_demo_cols = c("mat_age_bin", "mom_ethn_backgr_f2", "marital_status_f_di2", "education_level_f", "race_upd2")
# p_values_patient = sapply(mom_demo_cols, get_anova_p_patient, delivery_df=delivery_df)
# write.csv(p_values_patient, file.path(out_dir, "anova_patient.csv"))


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
