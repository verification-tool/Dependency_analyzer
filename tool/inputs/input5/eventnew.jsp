<%@ include file="Common.jsp" %><%!
//
//   Filename: EventNew.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/01
//

static final String sFileName = "EventNew.jsp";
              
static final String PageBODY = "bgcolor=\"#FFFFFF\" text=\"#000000\" link=\"#000080\" vlink=\"#000080\" alink=\"#000080\" background=\"images/bg.gif\" style=\"background-repeat: no-repeat\"";
static final String FormTABLE = "border=\"0\" cellspacing=\"1\" cellpadding=\"2\"";
static final String FormHeaderTD = "align=\"center\" bgcolor=\"#0033CC\"";
static final String FormHeaderFONT = "style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String FieldCaptionTD = "bgcolor=\"#0066FF\"";
static final String FieldCaptionFONT = "style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String DataTD = "";
static final String DataFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String ColumnFONT = "style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String ColumnTD = "bgcolor=\"#0066FF\"";
%><%

boolean bDebug = false;

String sAction = getParam( request, "FormAction");
String sForm = getParam( request, "FormName");
String sEventErr = "";

java.sql.Connection conn = null;
java.sql.Statement stat = null;
String sErr = loadDriver();
conn = cn();
stat = conn.createStatement();
if ( ! sErr.equals("") ) {
 try {
   out.println(sErr);
 }
 catch (Exception e) {}
}
if ( sForm.equals("Event") ) {
  sEventErr = EventAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sEventErr)) return;
}

%>            
<html>
<head>
<title>Events</title>
<meta name="GENERATOR" content="YesSoftware CodeCharge v.1.2.0 / JSP.ccp build 05/21/01"/>
<meta http-equiv="pragma" content="no-cache"/>
<meta http-equiv="expires" content="0"/>
<meta http-equiv="cache-control" content="no-cache"/>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
</head>
<body bgcolor="#FFFFFF" text="#000000" link="#000080" vlink="#000080" alink="#000080" background="images/bg.gif" style="background-repeat: no-repeat">
<jsp:include page="Header.jsp" flush="true"/>
 <table>
  <tr>
   
   <td valign="top">
<% Event_Show(request, response, session, out, sEventErr, sForm, sAction, conn, stat); %>
    
   </td>
  </tr>
 </table>


<center><font face="Arial"><small>This dynamic site was generated with <a href="http://www.codecharge.com">CodeCharge</a></small></font></center>
</body>
</html>
<%%>
<%
if ( stat != null ) stat.close();
if ( conn != null ) conn.close();
%>
<%!


  String EventAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sEventErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "Default.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      String pPKevent_id = "";
      if (sAction.equalsIgnoreCase("cancel") ) {
        try {
          if ( stat != null ) stat.close();
          if ( conn != null ) conn.close();
        }
        catch ( java.sql.SQLException ignore ) {}
        response.sendRedirect (sActionFileName);
        return "sendRedirect";
      }

      final int iinsertAction = 1;
      final int iupdateAction = 2;
      final int ideleteAction = 3;
      int iAction = 0;

      if ( sAction.equalsIgnoreCase("insert") ) { iAction = iinsertAction; }
      if ( sAction.equalsIgnoreCase("update") ) { iAction = iupdateAction; }
      if ( sAction.equalsIgnoreCase("delete") ) { iAction = ideleteAction; }

     


      String fldeventid="";
      String fldno_of_days="";
      String fldyear="";
      String fldno_of_presenters="";
      String fldno_of_perticipants="";


      // Load all form fields into variables
    
      fldeventid = getParam(request, "eventid");
      fldno_of_days = getParam(request, "no_of_days");
      fldyear = getParam(request, "year");
      fldno_of_presenters = getParam(request, "no_of_presenters");
      fldno_of_perticipants = getParam(request, "no_of_perticipants");
     
      // Validate fields
      if ( iAction == iinsertAction || iAction == iupdateAction ) {
        if ( isEmpty(fldeventid) ) {
          sEventErr = sEventErr + "The value in field Name* is required.<br>";
        }
        if ( isEmpty( fldno_of_days) ) {
          sEventErr = sEventErr + "The value in field Category* is required.<br>";
        }
        if ( isEmpty( fldyear) ) {
          sEventErr = sEventErr + "The value in field Location* is required.<br>";
        }
        if ( isEmpty(fldno_of_presenters) ) {
          sEventErr = sEventErr + "The value in field Date Start* is required.<br>";
        }
        if ( ! isNumber(fldno_of_perticipants)) {
          sEventErr = sEventErr + "The value in field Category* is incorrect.<br>";
        }
        if (sEventErr.length() > 0 ) {
          return (sEventErr);
        }
      }


     
      


      if ( sEventErr.length() > 0 ) return sEventErr;
      try {
        // Execute SQL statement
       // stat.executeUpdate(sSQL);

        stat.executeUpdate("update events set no_of_days = no_of_days + 1 where no_of_presenters >= 20");

        stat.executeUpdate("update events set no_of_days = no_of_days - 1 where no_of_presenters <= 14");

        stat.executeUpdate("delete from events where no_of_presenters  <= 4");
       
         java.sql.ResultSet rs = null;

         stat.executeUpdate("update events set no_of_presenters = no_of_presenters + 1 where no_of_days > 5");

         stat.executeUpdate("delete from events where no_of_presenters < 10");

        stat.executeUpdate("insert into events (no_of_presenters, no_of_days) values (25, 7)"); 
      
       // Open recordset

        rs = openrs( stat, "SELECT * From events WHERE no_of_presenters >= 1 ");
        



         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



        while(rs.next()){

        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        
            
        fldeventid = (String) rsHash.get("eventid");
        bw.write(fldeventid);
        fldyear = (String) rsHash.get("year");
        bw.write(fldyear);
        fldno_of_days = (String) rsHash.get("no_of_days");
        bw.write(fldno_of_days);
        fldno_of_presenters = (String) rsHash.get("no_of_presenters");
        bw.write(fldno_of_presenters);
        fldno_of_perticipants = (String) rsHash.get("no_of_perticipants");
        bw.write(fldno_of_perticipants);

      }
      rs.close();    

      }
      catch(java.sql.SQLException e) {
        sEventErr = e.toString(); return (sEventErr);
      }
  
      try {
        if ( stat != null ) stat.close();
        if ( conn != null ) conn.close();
      }
      catch ( java.sql.SQLException ignore ) {}
      response.sendRedirect (sActionFileName);

      return "sendRedirect";
    }
    catch (Exception e) {out.println(e.toString()); }
    return (sEventErr);
  }

  


  void Event_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sEventErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
    try {

      String sSQL="";
      String sQueryString = "";
      String sPage = "";
      String sWhere = "";
      String transitParams = "";
      String transitParamsHidden = "";
      String requiredParams = "";
      String primaryKeyParams ="";
      java.util.Hashtable rsHash = new java.util.Hashtable();
      
      String pevent_id = "";

      
      String fldeventid="";
      String fldyear="";
      String fldno_of_days="";
      String fldno_of_presenters="";
      String fldno_of_perticipants="";
      


      boolean bPK = true;

      if ( "".equals(sEventErr)) {
        // Load primary key and form parameters
        //fldcategory_id = getParam( request, "category_id");
        pevent_id = getParam( request, "eventid");
      }
      else {
        // Load primary key, form parameters and form fields
        fldeventid = getParam( request, "eventid");
        
        fldyear = getParam( request, "year");
        fldno_of_days = getParam( request, "no_of_days");
        fldno_of_presenters = getParam( request, "no_of_presenters");
        fldno_of_perticipants = getParam( request, "no_of_perticipants");
        
      }

      
      //if ( isEmpty(pevent_id)) { bPK = false; }
      
      //sWhere += "event_id=" + toSQL(pevent_id, adNumber);
      //primaryKeyParams += "<input type=\"hidden\" name=\"PK_event_id\" value=\""+pevent_id+"\"/>";

     // sSQL = "select * from events where " + sWhere;


      out.println("    <table border=\"0\" cellspacing=\"1\" cellpadding=\"2\">");
      
      if ( ! sEventErr.equals("")) {
        out.println("     <tr>\n      <td  colspan=\"2\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">"+sEventErr+"</font></td>\n     </tr>");
      }
      sEventErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"Event\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "Event".equals(sForm))) {

        // Open recordset
        rs = openrs( stat, sSQL);
        rs.next();
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        rs.close();
        fldeventid = (String) rsHash.get("eventid");
        if ( "".equals(sEventErr)) {
          // Load data from recordset when form displayed first time
          fldeventid = getParam( request, "eventid");
        
        fldyear = getParam( request, "year");
        fldno_of_days = getParam( request, "no_of_days");
        fldno_of_presenters = getParam( request, "no_of_presenters");
        fldno_of_perticipants = getParam( request, "no_of_perticipants");
        }

        if (sAction.equals("") || ! "Event".equals(sForm)) {
      
          fldeventid = getParam( request, "eventid");
        
        fldyear = getParam( request, "year");
        fldno_of_days = getParam( request, "no_of_days");
        fldno_of_presenters = getParam( request, "no_of_presenters");
        fldno_of_perticipants = getParam( request, "no_of_perticipants");
        }
        
      }
      else {
        if ( "".equals(sEventErr)) {
          fldcategory_id = toHTML(getParam(request,"category_id"));
        }
flddate_start= new java.text.SimpleDateFormat("yyyy-MM-dd hh:mm:ss").format(new java.util.Date());
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Name*</font></td><td >"); out.print("<input type=\"text\"  name=\"name\" maxlength=\"50\" value=\""+toHTML(fldname)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Category*</font></td><td >"); 
      out.print("<select name=\"category_id\">"+getOptions( conn, "select category_id, category_desc from categories order by 2",false,true,fldcategory_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Location*</font></td><td >"); out.print("<textarea name=\"location\" cols=\"50\" rows=\"3\">"+toHTML(fldlocation)+"</textarea>");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Date Start*</font></td><td >"); out.print("<input type=\"text\"  name=\"date_start\" maxlength=\"15\" value=\""+toHTML(flddate_start)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Date End</font></td><td >"); out.print("<input type=\"text\"  name=\"date_end\" maxlength=\"15\" value=\""+toHTML(flddate_end)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Presenter</font></td><td >"); out.print("<input type=\"text\"  name=\"presenter\" maxlength=\"50\" value=\""+toHTML(fldpresenter)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#0066FF\"><font style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica\">Description</font></td><td >"); out.print("<textarea name=\"description\" cols=\"50\" rows=\"5\">"+toHTML(flddescription)+"</textarea>");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "Event".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.Event.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Event\"><input type=\"hidden\" value=\"\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Insert\" onclick=\"document.Event.FormAction.value = 'insert';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.Event.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Event\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"event_id\" value=\""+toHTML(fldeventid)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>