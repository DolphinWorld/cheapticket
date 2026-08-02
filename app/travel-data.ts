export const airports: Record<string,string> = {
  NYC:"New York City area", JFK:"John F. Kennedy International", LGA:"LaGuardia", EWR:"Newark Liberty International", HPN:"Westchester County", SWF:"New York Stewart International",
  SEA:"Seattle–Tacoma International", PAE:"Seattle Paine Field", DFW:"Dallas Fort Worth International", DAL:"Dallas Love Field", LAX:"Los Angeles International", SFO:"San Francisco International", ORD:"Chicago O’Hare International", MDW:"Chicago Midway", BOS:"Boston Logan International", IAD:"Washington Dulles International", DCA:"Reagan Washington National", ATL:"Hartsfield–Jackson Atlanta International", DEN:"Denver International", MIA:"Miami International", MCO:"Orlando International", LAS:"Harry Reid International", PHX:"Phoenix Sky Harbor International"
};
export const airlines: Record<string,string> = { AA:"American Airlines", AS:"Alaska Airlines", B6:"JetBlue", DL:"Delta Air Lines", F9:"Frontier Airlines", HA:"Hawaiian Airlines", NK:"Spirit Airlines", UA:"United Airlines", WN:"Southwest Airlines" };
export const airportName=(code:string)=>airports[code]??"Airport or metro code";
export const airlineName=(code:string)=>airlines[code]??"Airline code";
