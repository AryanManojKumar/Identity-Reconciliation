from sqlalchemy.orm import Session
from models import Contact, LinkPrecedence
from datetime import datetime

def identify_contact(db: Session, email: str = None, phoneNumber: str = None):
    # Find all contacts matching email or phone
    contacts = db.query(Contact).filter(
        Contact.deletedAt.is_(None),
        ((Contact.email == email) if email else False) | 
        ((Contact.phoneNumber == phoneNumber) if phoneNumber else False)
    ).order_by(Contact.createdAt).all()
    
    if not contacts:
        # No existing contact, create new primary
        new_contact = Contact(
            email=email,
            phoneNumber=phoneNumber,
            linkPrecedence=LinkPrecedence.primary
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return build_response(db, new_contact.id)
    
    # Get all primary contacts from the matches
    primary_ids = set()
    for contact in contacts:
        if contact.linkPrecedence == LinkPrecedence.primary:
            primary_ids.add(contact.id)
        elif contact.linkedId:
            primary_ids.add(contact.linkedId)
    
    # Find the oldest primary
    primary_id = min(primary_ids) if primary_ids else contacts[0].id
    
    # If multiple primaries exist, merge them
    if len(primary_ids) > 1:
        for pid in primary_ids:
            if pid != primary_id:
                # Convert this primary to secondary
                contact_to_update = db.query(Contact).filter(Contact.id == pid).first()
                contact_to_update.linkPrecedence = LinkPrecedence.secondary
                contact_to_update.linkedId = primary_id
                contact_to_update.updatedAt = datetime.utcnow()
                
                # Update all its secondaries to point to the new primary
                db.query(Contact).filter(Contact.linkedId == pid).update({
                    "linkedId": primary_id,
                    "updatedAt": datetime.utcnow()
                })
        db.commit()
    
    # Check if we need to create a new secondary contact
    existing_match = False
    for contact in contacts:
        if contact.email == email and contact.phoneNumber == phoneNumber:
            existing_match = True
            break
    
    if not existing_match:
        # New information, create secondary
        new_secondary = Contact(
            email=email,
            phoneNumber=phoneNumber,
            linkedId=primary_id,
            linkPrecedence=LinkPrecedence.secondary
        )
        db.add(new_secondary)
        db.commit()
    
    return build_response(db, primary_id)

def build_response(db: Session, primary_id: int):
    # Get primary contact
    primary = db.query(Contact).filter(
        Contact.id == primary_id,
        Contact.deletedAt.is_(None)
    ).first()
    
    # Get all secondary contacts
    secondaries = db.query(Contact).filter(
        Contact.linkedId == primary_id,
        Contact.deletedAt.is_(None)
    ).order_by(Contact.createdAt).all()
    
    # Collect unique emails and phones
    emails = []
    phones = []
    
    if primary.email and primary.email not in emails:
        emails.append(primary.email)
    if primary.phoneNumber and primary.phoneNumber not in phones:
        phones.append(primary.phoneNumber)
    
    secondary_ids = []
    for sec in secondaries:
        secondary_ids.append(sec.id)
        if sec.email and sec.email not in emails:
            emails.append(sec.email)
        if sec.phoneNumber and sec.phoneNumber not in phones:
            phones.append(sec.phoneNumber)
    
    return {
        "contact": {
            "primaryContatctId": primary_id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }
