Feature: US033 View full address in summary box in digital register

#Acceptance Criteria
 # Be able to display the full address - (for the show and tell)
 # The address must be in the same format as when displayed on the Gov.UK Property Pages
 # If the information relating to the address is not available then a meaningful message must    be displayed

@US033 @DigitalRegistry
Scenario: Title number on property title
  Given I am a citizen
  And I have logged in
  And I have a property
  When I view the property detail page
  Then I see the title number of the property

@US033  @ViewFullAddress @DigitalRegistry
Scenario: Full address on property title
  Given I am a citizen
  And I have logged in
  And I have a property
  When I view the property detail page
  Then I see the full address of the property

@US033 @No_Address_Data @DigitalRegistry
Scenario: No property title available
  Given I am a citizen
  And I have logged in
  And I do not have a property
  When I view the property detail page
  Then I get a page not found message
