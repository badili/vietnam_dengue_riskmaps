# options(repos = c('https://mirrors.ebi.ac.uk/CRAN/'))
# install.packages("maptools")
# install.packages("spdep")
# install.packages("rgdal")
# install.packages("raster")
# install.packages("rgeos")
# install.packages("INLA", repos="https://www.math.ntnu.no/inla/R/stable")
# install.packages("ggplot2")
# install.packages("doBy")
# install.packages("plot3D")
# install.packages("ggmap")
# install.packages("GISTools")
# 
# Package for dealing with large dataset
# install.packages("devtools")
# library(devtools)
# install_github("Nowosad/spDataLarge")

# prcomp()

print("Loading the required libraries...")
library(maptools)
library(spdep)
library(rgdal)
library(raster)
library(rgeos)
library(INLA)
library(doBy)
library(ggplot2)
library(plot3D)
library(mapproj)
library(scales)
library(GISTools)
library(rgeos)
library(sp)

print("Change the current working directory to the current directory...")
working_dir = "./"

setwd(working_dir)

#import data
map <- readOGR(paste(working_dir, "maps/Provinces.shp", sep=""))

#spatial relationships
print("Read the spatial relationships and the shape files in...")
map <- readOGR(paste(working_dir, "maps/Provinces.shp", sep=""))
newmap <- spTransform(map, CRS("+proj=utm +zone=48N ellps=WGS84"))
map$idmap <- 1:nrow(map) #generate provinces ids

print("Load the map...")
viet.map<-map
temp <- poly2nb(viet.map, queen = FALSE)
print("Do some crazy things...")
nb2INLA("v.graph", temp)
viet.adj <- paste(getwd(),"/v.graph",sep="")
weights <- nb2listw(temp, style="W")

print("Plot the map and graph")
plot(map, lwd=1)
plot(temp, coordinates(map), add=TRUE, col="blue", lty=2)

#data for modelling
print("Read in the data for modelling...")
dengue4<-read.csv("dengue4.csv", header=TRUE)
data<-data.frame(province=dengue4$province.x, year=dengue4$year,month=dengue4$month,time=dengue4$time,
                 case=as.integer(dengue4$cases),pop=dengue4$pop,evaporation=dengue4$evaporation,
                 w.velocity=dengue4$wind_veloc,rain=dengue4$rain, max.rain=dengue4$rain_max, 
                 av.temp=dengue4$av_temp, av.max.temp=dengue4$av_max_temp, min.temp=dengue4$min_tem,
                 abs.maxtemp=dengue4$abs_max_temp, ab.min.temp=dengue4$ab_min_temp, rel.humid=dengue4$rel_humid,
                 abs.min.humid=dengue4$abs_minhumidity, dur.sun=dengue4$dura_sunshine, idmap=dengue4$idmap, 
                 idmap2=dengue4$idmap, time2=dengue4$time, rainl1=dengue4$lagrain1, 
                 rainl2=dengue4$lagrain2,rainl3=dengue4$lagrain3, alt=dengue4$altitude, 
                 totcult=dengue4$totcult,rfcult=dengue4$rfcult, ircult=dengue4$ircult, 
                 gwood=dengue4$gwood, urban=dengue4$urban, 
                 water=dengue4$water, popden=dengue4$popden,tmin.lag1=dengue4$tmin_l1,
                 tmin.lag2=dengue4$tmin_l2, tmin_lag3=dengue4$tmin_l3, nino=dengue4$nino, nino_l1=dengue4$nino_l1,
                 nino_l2=dengue4$nino_l2, nino_lag3=dengue4$nino_l3, perc_wet=dengue4$wet_perc, 
                 perc_forest=dengue4$forest_perc, perc_shrub=dengue4$shrub_perc, perc_savana=dengue4$savana_perc,
                 perc_crop=dengue4$crop_perc, perc_urban=dengue4$urban_perc)

# names(data)

#####>>>>>>>>>> SPACE TIME INTERACTIONS -- TYPE II  <<<<<########
print("Computing space and time interactions - Type II")
ID.area.int<-data$idmap
ID.year.int<-data$time

# names(data)
formula2<-case~1+tmin.lag2+I(tmin.lag2^2)+I(rainl2/100)+I((rainl2/100)^2)+alt+perc_urban+I(perc_urban^2)+perc_crop+
  f(idmap, model="bym", graph=viet.adj)+
  f(time, model="ar1")+
  f(ID.area.int,model="iid", group=ID.year.int,
    control.group = list(model="ar1"))

mod2 <- inla(formula2,family="poisson",data=data, E=popden,
                    verbose=TRUE, control.compute=list(dic=TRUE),
                    control.predictor = list(compute = TRUE))

# summary(mod2)
######################################################################################
data.pred<-as.data.frame(c(dengue4, mod2$summary.fitted))
# names(data.pred)
nrow(data.pred)
names(mod2$summary.fitted)

print("Load the plyr library")
library(plyr)
# names(data.pred)
data.pred<-rename(data.pred, c("X0.025quant"="low.quant","X0.5quant"="mid.quant","X0.975quant"="upper.quant"))
# nrow(data.pred)
print("Write the predictions to a csv file...")
write.csv(data.pred, "data_pred.csv")

##overall map
# names(data.pred)
print("Create the overall map")
globalmean<-summaryBy(mean+low.quant+upper.quant~idmap, data = data.pred,FUN = function(x) { c(m = mean(as.numeric(x), na.rm=TRUE))})
globalmean<-rename(globalmean, c("mean.m"="mean","low.quant.m"="lower_quantile","upper.quant.m"="upper_quantile"))

map.f<-fortify(map, region="idmap")
data_glo<-merge(map.f, globalmean, by.x="id",by.y="idmap"); 
final_glo<-data_glo[order(data_glo$order), ]
# head(final_glo)
write.csv(final_glo, "final_glo.csv")

###########>>>>MEAN
print("Calculating the mean...")
ggplot()+
  geom_polygon(data = final_glo, 
               aes(x = long, y = lat, group = group, fill=mean), 
               color = "black", size = 0.25) + 
scale_fill_distiller(palette = "YlOrRd", direction=1, breaks = pretty_breaks(n = 6),
                     limits=c(0,2))+
  coord_map()+theme_bw()+theme(legend.position = c(0.25,.4))+
  theme(legend.key.height=unit(.2, "cm"))+theme(legend.key.width=unit(.2, "cm"))+
  theme(legend.title=element_text(size=4))+theme(legend.text=element_text(size=3))+
  xlab("Longitude")+ylab("Latitude")+
  theme(axis.title.x =element_text(size=4))+theme(axis.title.y =element_text(size=4))+
  theme(axis.text.x =element_text(size=3))+theme(axis.text.y=element_text(size=3))

dev.off()

##########>>>>lower quantile
print("Calculating the lower quantile...")
tiff("global_mean_lq.tiff", width=6, height=6, units="cm", res=300)

ggplot()+
  geom_polygon(data = final_glo, 
               aes(x = long, y = lat, group = group, fill=lower_quantile), 
               color = "black", size = 0.25) + 
  scale_fill_distiller(palette = "YlOrRd", direction=1, breaks = pretty_breaks(n = 6),
                       limits=c(0,2))+
  coord_map()+theme_bw()+theme(legend.position = c(0.3,.4))+
  theme(legend.key.height=unit(.2, "cm"))+theme(legend.key.width=unit(.2, "cm"))+
  theme(legend.title=element_text(size=4))+theme(legend.text=element_text(size=3))+
  xlab("Longitude")+ylab("Latitude")+
  theme(axis.title.x =element_text(size=4))+theme(axis.title.y =element_text(size=4))+
  theme(axis.text.x =element_text(size=3))+theme(axis.text.y=element_text(size=3))

dev.off()

#######>>>>>>>>Upper quantile
print("Calculating the upper quantile...")
tiff("global_mean_uq.tiff", width=6, height=6, units="cm", res=300)

ggplot()+
  geom_polygon(data = final_glo, 
               aes(x = long, y = lat, group = group, fill=upper_quantile), 
               color = "black", size = 0.25) + 
  scale_fill_distiller(palette = "YlOrRd", direction=1, breaks = pretty_breaks(n = 6),
                       limits=c(0,2))+
  coord_map()+theme_bw()+theme(legend.position = c(0.3,.4))+
  theme(legend.key.height=unit(.2, "cm"))+theme(legend.key.width=unit(.2, "cm"))+
  theme(legend.title=element_text(size=4))+theme(legend.text=element_text(size=3))+
  xlab("Longitude")+ylab("Latitude")+
  theme(axis.title.x =element_text(size=4))+theme(axis.title.y =element_text(size=4))+
  theme(axis.text.x =element_text(size=3))+theme(axis.text.y=element_text(size=3))

###################

## we can specify the month we want to map by subsetting the data