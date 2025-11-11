FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["MedScribe.DataApi.csproj", "."]
RUN dotnet restore "MedScribe.DataApi.csproj"
COPY . .
RUN dotnet build "MedScribe.DataApi.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "MedScribe.DataApi.csproj" -c Release -o /app/publish \
    /p:PublishReadyToRun=true \
    /p:InvariantGlobalization=true

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "MedScribe.DataApi.dll"]

