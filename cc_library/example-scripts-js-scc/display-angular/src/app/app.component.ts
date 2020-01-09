import { Component, OnInit } from "@angular/core";
import { HttpClient } from "@angular/common/http";
const SccLib = require("../../../../js-scc"); // development
// const SccLib = require("js-scc"); // production

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"]
})
export class AppComponent implements OnInit {
  title = "display";
  hint = "";
  scc;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      .get("assets/display_config.json")
      .toPromise()
      .then((response: any) => {
        const config = response;
        this.scc = new SccLib(config, 4, function(date, level, message) {
          const formatDate = function(date) {
            return (
              date.getDate() +
              "-" +
              date.getMonth() +
              1 +
              "-" +
              date.getFullYear() +
              " " +
              date.getHours() +
              ":" +
              date.getMinutes() +
              ":" +
              date.getSeconds()
            );
          };
          console.log(
            "time=" + formatDate(date) + " level=" + level + " msg=" + message
          ); // call own logger
        });
        // this.scc.publish("test", "hoi hoi");
      });
  }
}