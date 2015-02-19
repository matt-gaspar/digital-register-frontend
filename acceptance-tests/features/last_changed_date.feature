Feature: US027 Last Changed Date

#Acceptance Criteria
 # The date the application was last changed must be displayed

@US027 @DigitalRegistry
Scenario: Last changed date
  Given I am a citizen
  And I have logged in
  And I have a property
  When I view the property detail page
  Then I see the date at which the title was last changed
