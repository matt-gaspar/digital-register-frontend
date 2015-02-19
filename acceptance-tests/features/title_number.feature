Feature: US026 Title Number in the summary box in the digital register

#Acceptance Criteria
 # The title number associated with the property description is displayed in the summary box

@US026 @DigitalRegistry
Scenario: Title number on property title
  Given I am a citizen
  And I have logged in
  And I have a property
  When I view the property detail page
  Then I see the title number of the property
